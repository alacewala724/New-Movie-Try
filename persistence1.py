# persistence.py

import json
import os
from models import Movie

DATA_FILENAME = "movies.json"

class PersistenceManager:
    def __init__(self, filename=DATA_FILENAME):
        self.filename = filename

    def delete_movies(self):
        try:
            if os.path.exists(self.filename):
                os.remove(self.filename)
                return True
        except Exception as e:
            print("Error deleting movies:", e)
            return False

    def save_movies(self, movies):
        data = [movie.to_dict() for movie in movies]
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Error saving movies:", e)

    def load_movies(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            return [Movie.from_dict(d) for d in data]
        except Exception as e:
            print("Error loading movies:", e)
            return []
