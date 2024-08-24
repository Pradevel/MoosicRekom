import os
import spotipy
from dotenv import load_dotenv
from spotipy import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk
import re
import ssl
import random
import csv

# Load environment variables
load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# Set up Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')


# Define functions
def scrape_lyrics(song_name, artist_name):
    search_query = f"{song_name} {artist_name} lyrics site:gaana.com"
    search_results = search(search_query, num_results=5)
    headers = {'User-Agent': 'Mozilla/5.0'}

    for link in search_results:
        print(f"Attempting to fetch lyrics from: {link}")  # Debug info
        try:
            lyrics_page_response = requests.get(link, headers=headers)

            if lyrics_page_response.status_code != 200:
                continue
            lyrics_soup = BeautifulSoup(lyrics_page_response.text, 'html.parser')
            lyrics = extract_lyrics_from_p_tags(lyrics_soup)

            if lyrics:
                return lyrics
        except requests.exceptions.RequestException as e:
            continue

    return "Lyrics not found."


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
        'name': track_info['name'],
        'artists': [artist['name'] for artist in track_info['artists']],
        'album': track_info['album']['name'],
        'release_date': track_info['album']['release_date'],
        'energy': audio_features['energy'],
        'danceability': audio_features['danceability'],
        'popularity': track_info['popularity'],
    }
    return song_data


def append_dict_to_csv(file_path, data_dict, fieldnames):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)


# Define CSV file path and fieldnames
csv_file_path = 'song_data.csv'
fieldnames = ['name', 'artists', 'album', 'release_date', 'energy', 'danceability', 'popularity', 'keywords']

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

    # Specific Decades or Eras
    "90s Bollywood Songs",
    "80s Hindi Songs",
    "70s Hindi Classics",
    "Early 2000s Bollywood Hits",
    "Vintage Hindi Songs",

    # Genres and Moods
    "Romantic Hindi Songs",
    "Dance Hindi Songs",
    "Sad Hindi Songs",
    "Party Hindi Songs",
    "Melancholic Hindi Music",
    "Bollywood Romantic Ballads",
    "Hindi Rock Songs",
    "Hindi Folk Songs",
    "Bollywood Love Songs",

    # Popular Artists and Composers
    "Songs by Lata Mangeshkar",
    "Songs by Kishore Kumar",
    "A.R. Rahman Hits",
    "Songs by Arijit Singh",
    "Bollywood Songs by Shreya Ghoshal",

    # Specific Themes
    "Hindi Festival Songs (e.g., Diwali, Holi)",
    "Hindi Inspirational Songs",
    "Patriotic Hindi Songs",
    "Hindi Wedding Songs",

    # Playlists and Curated Collections
    "Bollywood Top 50",
    "Hindi Music for Relaxation",
    "Bollywood Essentials",
    "Hindi Hits of the Year",

    # Regional Variations
    "Punjabi Bollywood Songs",
    "South Indian Hindi Songs",
    "Hindi Songs from Mumbai",

    # Example Queries for API or Search
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
                    lyrics = scrape_lyrics(song_name, artist_name)
                    data['keywords'] = extract_keywords(lyrics)
                    data['artists'] = ', '.join(data['artists'])

                    append_dict_to_csv(csv_file_path, data, fieldnames)
    except Exception as e:
        print(f"Error processing playlist or track: {e}")
        continue

    if len(collected_tracks) >= 5000:
        break