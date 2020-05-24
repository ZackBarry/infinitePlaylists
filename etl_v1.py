import requests
import config as C
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
import os
import re


def get_access_token():
    #return 'BQD7ur_P_ehqnCkMt_xPPVggKXNiiXsK2-XhYmXGz3Xthysrgq5z98H7J8jb7VLrlp-0rFLPC-BHQYgpCf4'
    # use global variable so that only refreshes once every 3600 seconds (once per hour)
    # https://developer.spotify.com/documentation/ios/guides/token-swap-and-refresh/
    client_id, client_secret = C.default['client_id'], C.default['client_secret']

    url = 'https://accounts.spotify.com/api/token'
    grant_type = 'client_credentials'
    body_params = {'grant_type': grant_type}

    response = requests.post(url, data=body_params, auth=(client_id, client_secret))

    if response.status_code == 200:

        # Get the json data
        json_data = response.json()
        return json_data['access_token']

    else:
        print(f"{response.status_code} Error in API call")


def get_category_ids(categories_json):

    json_items = categories_json['categories']['items']

    if json_items == []:
        return json_items
    else:
        return pd.json_normalize(json_items)['id'].tolist()


def get_next_category_url(categories_json):

    return categories_json['categories']['next']


def get_categories(url='https://api.spotify.com/v1/browse/categories'):

    try:
        response = requests.get(
            url=url,
            headers={'Authorization': 'Bearer ' + get_access_token()}
        )
    except Exception as e:
        logging.exception(e)
        print(f"An error occurred with url {url}")
        return -1

    if response.status_code == 200:
        return response.json()

    else:
        print(f"{response.status_code} Error in API call")
        return -1


def get_all_category_ids():

    ids = []

    json_response = get_categories()

    while json_response != -1:
        new_ids = get_category_ids(json_response)
        if len(new_ids) == 0:
            break
        else:
            ids.extend(new_ids)
            url = get_next_category_url(json_response)
            json_response = get_categories(url)

    return ids


def get_category_playlists(category_id='', country='US', url='https://api.spotify.com/v1/browse/categories/{category_id}/playlists'):
    """
    Query spotify's API to get the songs contained in a playlist.
    """

    if category_id != '':
        url = url.replace("{category_id}", category_id)

    try:
        response = requests.get(
            url=url,
            params={'country': country},
            headers={'Authorization': 'Bearer ' + get_access_token()}
        )
    except Exception as e:
        logging.exception(e)
        print(f"An error occurred with url {url}")
        return -1

    if response.status_code == 200:
        return response.json()


def get_playlist(url):
    response = requests.get(
        url=url,
        headers={'Authorization': 'Bearer ' + get_access_token()}
    )
    return response.json()


def get_entire_playlist(playlist_id='42gxpKWSAzT5k05nIzP3O2'):

    url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id=playlist_id)

    json_response = get_playlist(url)
    df = pd.json_normalize(json_response['items'])
    next_url = json_response['next']

    while next_url is not None:
        json_response = get_playlist(next_url)
        df = df.append(pd.json_normalize(json_response['items']))
        next_url = json_response['next']

    return df


def get_playlist_details(playlist_id='42gxpKWSAzT5k05nIzP3O2'):

    df = get_entire_playlist(playlist_id)

    df_columns = df.columns.str
    album_cols = np.logical_and(df_columns.startswith('track.album'),
                                ~df_columns.startswith('track.album.artists'))
    artist_cols = df_columns.startswith('track.artists')
    playlist_cols = ~df_columns.startswith('track.')
    track_cols = np.logical_and.reduce((df_columns.startswith('track.'),
                                        ~df_columns.startswith('track.album.artists'),
                                        ~album_cols,
                                        ~artist_cols))
    track_id_col = df_columns.startswith('track.id')

    album_df_cols = np.logical_or(album_cols, track_id_col)
    artist_df_cols = np.logical_or(artist_cols, track_id_col)
    playlist_df_cols = np.logical_or(playlist_cols, track_id_col)
    track_df_cols = track_cols

    album_df = df[df.columns[album_df_cols]]
    artist_df = df[df.columns[artist_df_cols]]
    playlist_df = df[df.columns[playlist_df_cols]]
    track_df = df[df.columns[track_df_cols]]

    def expand_artist_rows(artist_row):
        df = pd.json_normalize(artist_row['track.artists'])
        df.insert(0, column='track.id', value=artist_row['track.id'])
        df.insert(0, column='artist_order', value=np.arange(len(df)))
        return df

    final_artist_df = pd.concat(
        [expand_artist_rows(artist_df.iloc[i]) for i in range(0, len(artist_df))]
    )

    playlist_df.insert(0, column='id', value=playlist_id)
    playlist_df.insert(1, column='track_no', value=np.arange(len(track_df)))

    album_df.columns = album_df.columns.str.replace('track.album.', '')
    album_df.columns = album_df.columns.str.replace('.', '_')
    final_artist_df.columns = final_artist_df.columns.str.replace('.', '_')
    playlist_df.columns = playlist_df.columns.str.replace('.', '_')
    track_df.columns = track_df.columns.str.replace('track.', '')
    track_df.columns = track_df.columns.str.replace('.', '_')



