# MoosicRekom

**MoosicRekom** is a Python project designed to collect and analyze music data from Spotify and Gaana. The primary goal is to create a dataset of songs with associated metadata and lyrics for further analysis or machine learning tasks.

## Features

- **Spotify Integration**: Fetches song data including name, artist, album, release date, energy, danceability, and popularity using the Spotify API.
- **Gaana Lyrics Scraper**: Scrapes song lyrics from Gaana based on the song name and artist.
- **Keyword Extraction**: Extracts keywords from the lyrics to identify prominent themes or terms.
- **CSV Output**: Saves collected data to a CSV file for easy access and analysis.

## Requirements

- Python 3.7 or higher
- Required Python libraries: `spotipy`, `requests`, `beautifulsoup4`, `nltk`, `selenium`, `chromedriver-autoinstaller`, `pandas`, `python-dotenv`, `google-search-python` (for search functionality)

## Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/MoosicRekom.git
    cd MoosicRekom
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory of the project and add your Spotify credentials:

    ```env
    SPOTIPY_CLIENT_ID=your_spotify_client_id
    SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
    ```

## Usage

1. **Run the Main Script**

    To start the data collection and analysis process, simply run:

    ```bash
    python main.py
    ```

    This script will:
    - Fetch playlists based on predefined queries from Spotify.
    - Retrieve song data and lyrics.
    - Extract keywords from lyrics.
    - Save the collected data to `song_data.csv`.

2. **Output**

    The collected song data and lyrics will be saved in `song_data.csv` with the following fields:
    - `id`: Spotify track ID
    - `name`: Song name
    - `artists`: List of artists
    - `album`: Album name
    - `release_date`: Release date
    - `energy`: Energy level of the song
    - `danceability`: Danceability score
    - `popularity`: Popularity score
    - `keywords`: Extracted keywords from lyrics

## Editing Queries

To customize the queries for fetching playlists and songs from Spotify, you can modify the `queries` list in the `main.py` file. Here’s how:

1. **Open `main.py`**

2. **Locate the Queries Section**

    Find the section where queries are defined, typically looking like this:

    ```python
    queries = [
        "Top Hits",
        "Chill Vibes",
        # Add or modify queries here
    ]
    ```

3. **Edit Queries**

    Add your desired queries or modify existing ones. For example:

    ```python
    queries = [
        "New Releases",
        "Trending Songs",
        "Workout Playlist",
        # Your custom queries
    ]
    ```

4. **Save and Run**

    After making changes, save the `main.py` file and re-run the script with:

    ```bash
    python main.py
    ```

## Troubleshooting

- **If you encounter a `429 Client Error` or `Rate Limit Exceeded` error**, you might be sending too many requests to Spotify or Gaana. Consider adding delays between requests or handling rate limits in your code.
- **If Gaana's website changes**, the CSS selectors used for scraping might need updates. Check the page source and update selectors accordingly.
- **For `NoSuchElementException`**: Ensure the selectors used to locate elements are accurate. Use browser developer tools to inspect the current structure of the web pages.

## Contributing

Contributions to the project are welcome! Please fork the repository and create a pull request with your proposed changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please contact [Pradevel](mailto:pratyushroy.whj@gmail.com).

---

Happy coding!