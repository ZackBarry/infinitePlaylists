import requests
import config as C
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
import os
import re


class Extract:

    def __init__(self):
        self.client_id = C.default['client_id']
        self.client_secret = C.default['client_secret']

    def get_access_token(self):
        # use global variable so that only refreshes once every 3600 seconds (once per hour)
        # https://developer.spotify.com/documentation/ios/guides/token-swap-and-refresh/
        url = 'https://accounts.spotify.com/api/token'
        body_params = {'grant_type': 'client_credentials'}

        response = requests.post(url, data=body_params, auth=(self.client_id, self.client_secret))

        if response.status_code == 200:

            # Get the json data
            json_data = response.json()
            return json_data['access_token']

        else:
            print(f"{response.status_code} Error in API call")

    def get_spotify_data(self, url):
        response = requests.get(
            url=url,
            headers={'Authorization': 'Bearer ' + Extract.get_access_token(self)}
        )
        return response.json()

    def get_playlist_data(self, params):
        # playlist_id='42gxpKWSAzT5k05nIzP3O2'

        url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id=params['playlist_id'])

        json_response = Extract.get_spotify_data(self, url)
        df = pd.json_normalize(json_response['items'])
        next_url = json_response['next']

        while next_url is not None:
            json_response = Extract.get_spotify_data(self, next_url)
            df = df.append(pd.json_normalize(json_response['items']))
            next_url = json_response['next']

        df.insert(0, column='id', value=params['playlist_id'])
        df.insert(0, column='track_no', value=np.arange(len(df)))
        return df

    def extract_spotify_data(self, what, params):
        if what == 'playlist':
            return Extract.get_playlist_data(self, params)
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

    PLAYLIST_COLS = [
        'id', 'track_no', 'track.id', 'added_at', 'primary_color',
        'added_by.href', 'added_by.id'
    ]

    def __init__(self, what, params_list):
        # param_list is a list of dicts, e.g. Transform('playlist', [{'playlist_id': '42gxpKWSAzT5k05nIzP3O2'}])

        extract_obj = Extract()
        self.what = what
        self.params_list = params_list

        data = [extract_obj.extract_spotify_data(self.what, params=params) for params in self.params_list]  # if check_condition(params)

        self.albums = pd.concat(
            [Transform.get_albums_from_playlist(df=df) for df in data]
        )
        self.artists = pd.concat(
            [Transform.get_artists_from_playlist(df=df) for df in data]
        )
        self.playlists = pd.concat(
            [Transform.get_playlist_from_playlist(df=df) for df in data]
        )
        self.tracks = pd.concat(
            [Transform.get_tracks_from_playlist(df=df) for df in data]
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

    def __init__(self, s3_bucket):



    def

