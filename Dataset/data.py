import csv
import os
import random
import re
import ssl
import time
import urllib
from collections import Counter

import nltk
import requests
import spotipy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from spotipy import SpotifyClientCredentials

# Load environment variables
load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# Set up Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Download NLTK resources
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')


def search_gaana_lyrics(song_name, artist_name):
    search_query = f"{song_name} {artist_name}"
    encoded_query = urllib.parse.quote(search_query)
    search_url = f"https://gaana.com/search/{encoded_query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        song_card = soup.find('li', class_='card')
        if not song_card:
            print("No song card found")
            return "Lyrics not found."

        song_link = song_card.find('a')['href']
        if not song_link:
            print("No song link found")
            return "Lyrics not found."

        song_url = urllib.parse.urljoin(search_url, song_link)
        song_response = requests.get(song_url, headers=headers)
        song_response.raise_for_status()
        song_soup = BeautifulSoup(song_response.text, 'html.parser')
        lyrics = extract_lyrics_from_p_tags(song_soup)

    except Exception as e:
        print(f"An error occurred: {e}")
        lyrics = "Lyrics not found."
    return lyrics

def extract_lyrics_from_p_tags(soup):
    lyrics_lines = []
    p_tags = soup.find_all('p')
    for tag in p_tags:
        line = tag.get_text(separator="\n").strip()
        if len(line) > 5 and not re.search(r"http|www|©", line):
            lyrics_lines.append(line)
        if len(lyrics_lines) >= 8:
            break
    return "\n".join(lyrics_lines).strip()



def extract_keywords(text, num_keywords=10):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)

    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    word_counts = Counter(filtered_tokens)
    keywords = [word for word, count in word_counts.most_common(num_keywords)]
    return keywords


def search_playlists(query, limit=10):
    results = sp.search(q=query, type='playlist', limit=limit)
    playlists = results['playlists']['items']
    return playlists


def get_playlist_track_ids(playlist_id, limit=100):
    track_ids = []
    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
        tracks = results['items']
        if not tracks:
            break
        track_ids.extend(track['track']['id'] for track in tracks)
        offset += limit
        if len(track_ids) >= 5000:
            break
    return track_ids


def get_song_data(track_id):
    track_info = sp.track(track_id)
    audio_features = sp.audio_features(track_id)[0]

    song_data = {
        'id': track_id,
        'name': track_info['name'],
        'artists': [artist['name'] for artist in track_info['artists']],
        'album': track_info['album']['name'],
        'release_date': track_info['album']['release_date'],
        'energy': audio_features['energy'],
        'danceability': audio_features['danceability'],
        'popularity': track_info['popularity'],
    }
    return song_data


def handle_rate_limits(response_headers):
    if 'Retry-After' in response_headers:
        wait_time = int(response_headers['Retry-After'])
        print(f"Rate limit reached. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
    else:
        print("Waiting for 5 seconds to avoid hitting the rate limit...")
        time.sleep(5)


def append_dict_to_csv(file_path, data_dict, fieldnames):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)


# Define CSV file path and fieldnames
csv_file_path = "song_data.csv"
fieldnames = ['id', 'name', 'artists', 'album', 'release_date', 'energy', 'danceability', 'popularity', 'keywords']

# Main logic
queries = [
    # General and Popular Keywords
    "Hindi Bollywood Hits",
    "Top Bollywood Songs",
    "Popular Hindi Songs",
    "Classic Hindi Songs",
    "Latest Hindi Songs",
    "Bollywood Music Playlist",
    "Top Hindi Tracks",
    "Hit Hindi Songs",
    "Hindi Movie Songs",
    "Hindi Love Songs",
    "90s Bollywood Songs",
    "80s Hindi Songs",
    "70s Hindi Classics",
    "Early 2000s Bollywood Hits",
    "Vintage Hindi Songs",
    "Romantic Hindi Songs",
    "Dance Hindi Songs",
    "Sad Hindi Songs",
    "Party Hindi Songs",
    "Melancholic Hindi Music",
    "Bollywood Romantic Ballads",
    "Hindi Rock Songs",
    "Hindi Folk Songs",
    "Bollywood Love Songs",
    "Songs by Lata Mangeshkar",
    "Songs by Kishore Kumar",
    "A.R. Rahman Hits",
    "Songs by Arijit Singh",
    "Bollywood Songs by Shreya Ghoshal",
    "Hindi Festival Songs (e.g., Diwali, Holi)",
    "Hindi Inspirational Songs",
    "Patriotic Hindi Songs",
    "Hindi Wedding Songs",
    "Bollywood Top 50",
    "Hindi Music for Relaxation",
    "Bollywood Essentials",
    "Hindi Hits of the Year",
    "Punjabi Bollywood Songs",
    "South Indian Hindi Songs",
    "Hindi Songs from Mumbai",
    "Hindi Bollywood 90s Hits",
    "Top Romantic Hindi Songs of 2023",
    "Dance Hits Bollywood Playlist",
    "Popular Hindi Songs by Arijit Singh",
    "Classic 80s Bollywood Music"
]

random.shuffle(queries)
collected_tracks = set()

for q in queries:
    playlists = search_playlists(q)
    try:
        for p in playlists:
            print(f"Processing playlist: {p['id']}")
            tracks = get_playlist_track_ids(p['id'])
            for t in tracks:
                if len(collected_tracks) >= 5000:
                    break
                if t not in collected_tracks:
                    collected_tracks.add(t)
                    data = get_song_data(t)
                    print(f"Processing song: {data['name']}")
                    song_name = data['name']
                    artist_name = random.choice(data['artists'])
                    lyrics = search_gaana_lyrics(song_name, artist_name)
                    data['keywords'] = extract_keywords(lyrics)
                    data['artists'] = ', '.join(data['artists'])

                    append_dict_to_csv(csv_file_path, data, fieldnames)
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error processing playlist or track: {e}")
        if e.http_status == 429:
            handle_rate_limits(e.headers)
        else:
            break
        continue

    if len(collected_tracks) >= 5000:
        break

