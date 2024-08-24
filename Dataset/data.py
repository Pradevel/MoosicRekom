import os

import spotipy
from dotenv import load_dotenv
from spotipy import SpotifyClientCredentials

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_data(track_id):
    track_info = sp.track(track_id)
    audio_features = sp.audio_features(track_id)[0]

    song_data = {
        'name': track_info['name'],
        'artists': [artist['name'] for artist in track_info['artists']],
        'album': track_info['album']['name'],
        'release_date': track_info['album']['release_date'],
        'energy': audio_features['energy'],
        'danceability': audio_features['danceability'],
        'popularity': track_info['popularity'],
    }
    return song_data

track_id = '3r8rpRYqxI77SFZZ4WCTXW'
song_data = get_song_data(track_id)
print(song_data)