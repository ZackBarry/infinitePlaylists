import requests
import config as C
import base64
import json
from datetime import datetime
import os

def get_playlist():
    """
    Query spotify's API to get the songs contained in a playlist.
    """

    # API key is defined in config.py
    parameters = {'appid':C.default['api_key']}

# Option 1

client_id, client_secret = C.default['client_id'], C.default['client_secret']
b64_key = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii'))
b64_key = b64_key.decode('utf-8')

url = 'https://accounts.spotify.com/api/token'
grant_type = 'client_credentials'
body_params = {'grant_type' : grant_type}

response = requests.post(
    url='https://accounts.spotify.com/api/token',
    data=body_params,
    headers={'Authorization': f"Basic {b64_key}"}
)

# Option 2

client_id, client_secret = C.default['client_id'], C.default['client_secret']

url = 'https://accounts.spotify.com/api/token'
grant_type = 'client_credentials'
body_params = {'grant_type' : grant_type}


response = requests.post(url, data=body_params, auth = (client_id, client_secret))

#

categories = requests.get(
    url='https://api.spotify.com/v1/browse/categories',
    params='',
    headers={'Authorization': 'Bearer ' + response.json()['access_token']}
)

