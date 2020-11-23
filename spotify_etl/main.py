import requests
import time
import numpy as np
from spotify_etl.spotify_plugins import *


def refresh_access_token(client_id, client_secret):
    """Retrieves a new Spotify API access token every 3400 seconds

    Spotify API access tokens are valid for 1 hr (3600 seconds).  An access token is stored in
    `self.access_token_string` until the difference between the current time and
    `self.access_token_time` exceeds 3400 seconds.

    https://joshspicer.com/spotify-now-playing

    Returns
    -------
    str
        API access token
    """

    now = int(time.time())  # seconds since epoch

    response = requests.post(
        url='https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(client_id, client_secret)
    )

    access_token = response.json()['access_token']

    # table.put_item(Item={'spotify': 'prod', 'expiresAt': now+3400, 'access_token': access_token})


def get_playlist(event, context):
    playlist_id = event['playlist_id']

    df = get_playlist_tracks(event)

    df = df.apply(extract_first_image, axis=1).drop(columns='track.album.images')
    df = df.apply(extract_first_artist_name, axis=1).drop(columns='track.artists')

    artist_df = get_artists_genres(list(df['track.artist.id']))
    df = df.merge(artist_df, on='track.artist.id', how='left')

    df.insert(0, column='track_no', value=np.arange(len(df)))
    df.insert(len(df.columns), column='playlist_id', value=playlist_id)

    df.columns = [col.replace('.', '_') for col in df.columns]

    df = df[['playlist_id', 'track_no', 'track_name', 'track_id', 'track_popularity',
             'track_album_name', 'track_album_image', 'track_artist', 'track_artist_id',
             'track_artist_followers_total', 'track_artist_genre_1', 'track_artist_genre_2']]

    return df
