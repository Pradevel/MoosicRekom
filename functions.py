import csv
import os
import ssl
import time
import re
from collections import Counter
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from spotify import sp

# Download NLTK resources
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')


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
