import requests
import pandas as pd
import boto3


def get_access_token():

    return '-1'


def get_spotify_data(url, params=None):
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
        headers={'Authorization': 'Bearer ' + get_access_token()},
        params=params
    )
    return response.json()


def extract_first_image(album_row):
    # The "track.album.image" column contains multiple image urls, only 1 is needed.
    album_row['track.album.image'] = album_row['track.album.images'][0]['url']
    return album_row


def extract_first_artist_name(artist_row):
    first_artist = artist_row['track.artists'][0]
    artist_row['track.artist'] = first_artist['name']
    artist_row['track.artist.id'] = first_artist['id']
    return artist_row


def get_artists_genres(artist_ids):
    """Retrieves artist information for a list of Spotify artist ids

    Parameters
    ----------
    artist_ids : list[str]
        List of Spotify album IDs to retrieve data for

    Returns
    -------
    pandas.core.frame.DataFrame
        Artist data, sourced from API JSON responses

    Examples
    --------
    get_artist_genres(artist_ids: ['1W8TbFzNS15VwsempfY12H'])
    """

    unique_artist_ids = list(set(artist_ids))
    # Can request up to 20 artists at a time from Spotify API
    twenty_ids = [unique_artist_ids[i:i + 20] for i in range(0, len(unique_artist_ids), 20)]
    params = [','.join(ids) for ids in twenty_ids]
    responses = [get_spotify_data('https://api.spotify.com/v1/artists', params={'ids': param}) for param in params]
    artist_lists = [response['artists'] for response in responses]
    single_artist_list = [item for sublist in artist_lists for item in sublist]
    artists_df = pd.json_normalize(single_artist_list)[['id', 'genres', 'followers.total']]

    artists_genres = pd.DataFrame(artists_df.genres.to_list(), index=artists_df.index)
    artists_genres.columns = [f'genre_{i+1}' for i in artists_genres.columns]
    if len(artists_genres.columns) == 1:
        artists_genres['genre_2'] = None
    artists_genres = artists_genres[['genre_1', 'genre_2']]

    artists_df = artists_df.drop(columns='genres')
    artists_df[['genre_1', 'genre_2']] = artists_genres
    artists_df.columns = [f'track.artist.{var}' for var in artists_df.columns]

    return artists_df


def get_playlist_tracks(playlist_id):
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
    items = ['track.name', 'track.artists', 'track.album.name', 'track.album.images', 'track.id', 'track.popularity']
    params = f"fields=items({','.join(items)}),next"

    json_response = get_spotify_data(url, params)
    df = pd.json_normalize(json_response['items'])
    next_url = json_response['next']

    while next_url is not None:
        json_response = get_spotify_data(next_url)
        df = df.append(pd.json_normalize(json_response['items']))
        next_url = json_response['next']

    return df
