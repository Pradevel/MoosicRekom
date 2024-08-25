import urllib
import requests
from bs4 import BeautifulSoup
from functions import extract_lyrics_from_p_tags


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

