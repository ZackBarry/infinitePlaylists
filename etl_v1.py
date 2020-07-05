import requests
import config as C
import pandas as pd
import numpy as np
from datetime import datetime
from time import time
import boto3


class Extract:
    """Extract various Spotify data via the Spotify API.  API credentials required.

    Attributes
    ----------
    client_id : str
        Spotify client id, obtained by registering an App with Spotify
    client_secret: str
        Spotify client secret, obtained by registering an App with Spotify
    access_token_time : int
        Seconds from epoch to when a Spotify access token was created
    access_token_string : str
        Access token for Spotify API
    """

    def __init__(self):
        self.client_id = C.default['client_id']
        self.client_secret = C.default['client_secret']
        self.access_token_time = None
        self.access_token_string = None

    def get_access_token(self):
        """Retrieves a new Spotify API access token every 3400 seconds

        Spotify API access tokens are valid for 1 hr (3600 seconds).  An access token is stored in
        `self.access_token_string` until the difference between the current time and
        `self.access_token_time` exceeds 3400 seconds.

        Returns
        -------
        str
            API access token
        """

        now = int(time())  # seconds since epoch

        # Check if the token needs to be refreshed.
        if self.access_token_time is None or now > self.access_token_time + 3400:
            self.access_token_time = now
            response = requests.post(
                url='https://accounts.spotify.com/api/token',
                data={'grant_type': 'client_credentials'},
                auth=(self.client_id, self.client_secret)
            )
            if response.status_code == 200:
                self.access_token_string = response.json()['access_token']
            else:
                self.access_token_string = None
                print(f"{response.status_code} Error in API call")

        return self.access_token_string

    def get_spotify_data(self, url, params=None):
        """Sends a GET request to the Spotify API

        Parameters
        ----------
        url : str
            The API endpoint to hit
        params : dict, optional
            Additional parameters to pass in the API request

        Returns
        -------
        pandas.core.frame.DataFrame


        """

        response = requests.get(
            url=url,
            headers={'Authorization': 'Bearer ' + self.get_access_token()},
            params=params
        )
        return response.json()

    def get_playlist_tracks(self, playlist_id):
        """Retrieves all tracks from a Spotify playlist

        Parameters
        ----------
        playlist_id : str
            Spotify ID of the playlist to retrieve

        Returns
        -------
        pandas.core.frame.DataFrame
            Track data from the Spotify playlist, sourced from API JSON response
        """

        url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id=playlist_id)

        json_response = self.get_spotify_data(url)
        df = pd.json_normalize(json_response['items'])
        next_url = json_response['next']

        while next_url is not None:
            json_response = self.get_spotify_data(next_url)
            df = df.append(pd.json_normalize(json_response['items']))
            next_url = json_response['next']

        df.insert(0, column='track_no', value=np.arange(len(df)))
        return df

    def get_playlist_metadata(self, playlist_id):
        """Retrieves metadata about a Spotify playlist

        Parameters
        ----------
        playlist_id : str
            Spotify ID of the playlist to retrieve

        Returns
        -------
        pandas.core.frame.DataFrame
            Playlist metadata, sourced from API JSON response
        """

        url = 'https://api.spotify.com/v1/playlists/{playlist_id}'.format(playlist_id=playlist_id)
        params = {'fields': 'id,name,owner,description,followers'}
        json_response = self.get_spotify_data(url, params)

        return pd.json_normalize(json_response)

    def get_playlist_data(self, playlist_id):
        """Retrieves metadata and track data for a Spotify playlist

        Examples
        --------
        get_playlist_data(playlist_id='42gxpKWSAzT5k05nIzP3O2')

        Parameters
        ----------
        playlist_id : str
            Spotify ID of the playlist to retrieve data for

        Returns
        -------
        pandas.core.frame.DataFrame
            Playlist metadata and track data, source from API JSON responses
        """

        metadata = self.get_playlist_metadata(playlist_id)
        tracks = self.get_playlist_tracks(playlist_id)

        return metadata.assign(foo=1).merge(tracks.assign(foo=1)).drop('foo', 1).reset_index()

    def extract_spotify_data(self, what, params):
        """Calls the appropriate `get_xxx_data()` function(s) for the given parameters

        Examples
        --------
        extract_spotify_data('playlist', '42gxpKWSAzT5k05nIzP3O2')

        Parameters
        ----------
        what : str
            Spotify object type to extract (currently, only 'playlist' is supported
        params
            Parameters required to access the Spotify object, an id is always required

        Returns
        -------
        pandas.core.frame.DataFrame
            Spotify data sourced from API JSON response(s)"""

        if what == 'playlist':
            return self.get_playlist_data(params)
        else:
            return -1


class Transform:

    ALBUM_COLS = [  # need to condense album.images
        'track.album.id', 'track.album.name', 'track.album.album_type',
        'track.album.release_date', 'track.album.total_tracks', 'track.album.images',
        'track.album.href', 'track.album.uri'
    ]

    ARTIST_COLS = [
        'track.artists', 'track.id'
    ]

    TRACK_COLS = [
        'track.id', 'track.name', 'track.explicit',
        'track.popularity', 'track.duration_ms',
        'track.album.id', 'track.disc_number', 'track.track_number',
        'track.href', 'track.uri'
    ]
    # TODO: update playlist columns to include more metadata
    PLAYLIST_COLS = [
        'id', 'track_no', 'track.id', 'added_at', 'primary_color',
        'added_by.href', 'added_by.id'
    ]

    def __init__(self, what, params_list):
        # param_list is a list of dicts, e.g. Transform('playlist', ['42gxpKWSAzT5k05nIzP3O2', '42gxpKWSAzT5k05nIzP3O2'])

        extract_obj = Extract()
        self.what = what
        self.params_list = params_list

        raw_data = [extract_obj.extract_spotify_data(self.what, params=params) for params in self.params_list]  # if check_condition(params)

        self.data = {}

        self.data['albums'] = pd.concat(
            [Transform.get_albums_from_playlist(df=df) for df in raw_data]
        )
        self.data['artists'] = pd.concat(
            [Transform.get_artists_from_playlist(df=df) for df in raw_data]
        )
        self.data['playlists'] = pd.concat(
            [Transform.get_playlist_from_playlist(df=df) for df in raw_data]
        )
        self.data['tracks'] = pd.concat(
            [Transform.get_tracks_from_playlist(df=df) for df in raw_data]
        )

    @staticmethod
    def get_albums_from_playlist(df):

        def extract_first_image(album_row):
            album_row['track.album.image'] = album_row['track.album.images'][0]['url']
            return album_row

        out_df = df[Transform.ALBUM_COLS]
        out_df = out_df.apply(extract_first_image, axis=1).drop(columns='track.album.images')
        out_df.columns = out_df.columns.str.replace('track.album.', '')
        out_df.columns = out_df.columns.str.replace('.', '_')
        return out_df

    @staticmethod
    def get_artists_from_playlist(df):

        def expand_artist_rows(artist_row):
            artist_df = pd.json_normalize(artist_row['track.artists'])
            artist_df.insert(0, column='track.id', value=artist_row['track.id'])
            artist_df.insert(0, column='artist_order', value=np.arange(len(artist_df)))
            return artist_df

        out_df = df[Transform.ARTIST_COLS]
        out_df = pd.concat(
            [expand_artist_rows(out_df.iloc[i]) for i in range(0, len(out_df))]
        )
        out_df.columns = out_df.columns.str.replace('.', '_')

        return out_df

    @staticmethod
    def get_playlist_from_playlist(df):
        out_df = df[Transform.PLAYLIST_COLS]
        out_df.columns = out_df.columns.str.replace('.', '_')
        return out_df

    @staticmethod
    def get_tracks_from_playlist(df):
        out_df = df[Transform.TRACK_COLS]
        out_df.columns = out_df.columns.str.replace('track.', '')
        out_df.columns = out_df.columns.str.replace('.', '_')
        return out_df


class Load:

    # Load('playlist', ['42gxpKWSAzT5k05nIzP3O2', '42gxpKWSAzT5k05nIzP3O2'], 'infinite-playlists')

    def __init__(self, what, params_list, s3_bucket_name):

        self.now = datetime.now().strftime('%d%m%y_%H%M%S')

        Load.check_or_add_bucket(s3_bucket_name)
        self.s3_bucket_name = s3_bucket_name

        self.transform_obj = Transform(what, params_list)

    def load(self):

        for key in self.transform_obj.data.keys():
            file_name = 's3://{bucket_name}/{data_type}/{timestamp}.csv'.format(
                bucket_name=self.s3_bucket_name,
                data_type=key,
                timestamp=self.now
            )
            self.transform_obj.data[key].to_csv(file_name, index=False)

    @staticmethod
    def check_or_add_bucket(s3_bucket_name):
        s3 = boto3.resource('s3')
        if s3.Bucket(s3_bucket_name) not in s3.buckets.all():
            s3.create_bucket(Bucket=s3_bucket_name, CreateBucketConfiguration={
                'LocationConstraint': 'us-west-2'})



