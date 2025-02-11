# api_client.py

import requests

TMDB_API_KEY = "1b707e00ba3e60f3b0bbcb81a6ae5f21"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie/{}"

class TMDBClient:
    def __init__(self, api_key=TMDB_API_KEY):
        self.api_key = api_key

    def search_movies(self, query):
        params = {"api_key": self.api_key, "query": query, "language": "en-US", "page": 1}
        try:
            response = requests.get(TMDB_SEARCH_URL, params=params, timeout=5)
            response.raise_for_status()
            return response.json().get("results", [])[:5]
        except Exception as e:
            print("Error searching movies:", e)
            return []

    def get_movie_details(self, movie_id):
        try:
            url = TMDB_DETAILS_URL.format(movie_id)
            params = {"api_key": self.api_key}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print("Error fetching movie details:", e)
            return None
