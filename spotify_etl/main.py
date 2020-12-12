import requests
import time
import numpy as np
import pyarrow
from datetime import datetime
from spotify_etl.spotify_plugins import *


def lambda_handler(event, context):

    playlist_id = event['playlist_id']

    timestamp = datetime.now().strftime('%m%d%y_%H%M%S')

    tracks = get_playlist_tracks(playlist_id) \
        .apply(extract_first_image, axis=1).drop(columns='track.album.images') \
        .apply(extract_first_artist_name, axis=1).drop(columns='track.artists')

    artists = get_artists_genres(list(tracks['track.artist.id']))

    playlist = tracks.merge(artists, on='track.artist.id', how='left') \
        .assign(track_no=np.arange(len(tracks)),
                playlist_id=playlist_id)

    playlist.columns = [col.replace('.', '_') for col in playlist.columns]

    playlist = playlist[['playlist_id', 'track_no', 'track_name', 'track_id', 'track_popularity',
                         'track_album_name', 'track_album_image', 'track_artist', 'track_artist_id',
                         'track_artist_followers_total', 'track_artist_genre_1', 'track_artist_genre_2']]

    playlist.to_parquet(f's3://infinite-playlists-test/playlists/{timestamp}_{playlist_id}')

    return playlist
