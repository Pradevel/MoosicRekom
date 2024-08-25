import random

import spotipy

from functions import search_playlists, get_playlist_track_ids, append_dict_to_csv, extract_keywords, handle_rate_limits
from gaana import search_gaana_lyrics
from queries import queries
from spotify import get_song_data

# Define CSV file path and fieldnames
csv_file_path = "song_data.csv"
fieldnames = ['id', 'name', 'artists', 'album', 'release_date', 'energy', 'danceability', 'popularity', 'keywords']

queries = queries
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

