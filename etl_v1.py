import requests
import config as C
import pandas as pd
import logging
from pandas.io.json import json_normalize
import json
from datetime import datetime
import os


def get_access_token():

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




def get_category_playlists(category_id):
    """
    Query spotify's API to get the songs contained in a playlist.
    """

    requests.get(

    )


