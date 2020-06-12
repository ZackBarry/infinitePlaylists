import requests
import config as C
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
import os
import re



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

