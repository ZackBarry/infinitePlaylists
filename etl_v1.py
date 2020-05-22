import requests
import config as C
import pandas as pd
import numpy as np
import logging
from pandas.io.json import json_normalize
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


def get_playlist_songs(playlist_id='7Anb1HtKdhvK3Pb1d36f22'):
    # TODO: add paging here if a playlist has > 100 songs
    response = requests.get(
        url='https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id=playlist_id),
        headers={'Authorization': 'Bearer ' + get_access_token()}
    )

    return response

# response.json()['next'] to check if more than 100 tracks
# pd.json_normalize(result.json()['items'])


def get_playlist_details(playlist_id='7Anb1HtKdhvK3Pb1d36f22'):

    response = requests.get(
        url='https://api.spotify.com/v1/playlists/{playlist_id}'.format(playlist_id=playlist_id),
        headers={'Authorization': 'Bearer ' + get_access_token()}
    )

    return response

# pd.json_normalize(result.json())
# we just want track details, not details about who/when added the track
result = get_playlist_songs()
df = pd.json_normalize(result.json()['items'])
df = df.filter(regex='track.*')
track_df = df.filterdrop(regex='track.album.[a-zA-Z^{id}]')
df.insert(0, column='track_index', value=np.arange(len(df)))

track_df_cols = np.logical_or.reduce((
    df.columns.str.contains(r'^(?!track.album)'),
    df.columns.str.contains('track.album.id')
))

album_df_cols = df.columns.str.startswith('track.album')

artist_df_cols = np.logical_or(
    df.columns.str.startswith('track.artists'),
    df.columns.str.startswith('track.id')
)

track_df = df[df.columns[track_df_cols]]
album_df = df[df.columns[album_df_cols]]
artist_df = df[df.columns[artist_df_cols]]


# artists
art = df.iloc[0]['track.artists']
pd.json_normalize(art).keys()