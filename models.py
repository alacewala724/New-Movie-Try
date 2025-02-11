# models.py

class Movie:
    def __init__(self, title, rating=None, elo=1400):
        self.title = title
        self.rating = rating  # Expected to be "good", "okay", or "bad"
        self.elo = elo
        self.wins = 0
        self.losses = 0
        self.games_played = 0
        self.visible_score = 0.0

    def to_dict(self):
        return {
            "title": self.title,
            "rating": self.rating,
            "elo": self.elo,
            "wins": self.wins,
            "losses": self.losses,
            "games_played": self.games_played,
            "visible_score": self.visible_score,
        }
    
    @classmethod
    def from_dict(cls, d):
        movie = cls(d["title"], d.get("rating"), d.get("elo", 1400))
        movie.wins = d.get("wins", 0)
        movie.losses = d.get("losses", 0)
        movie.games_played = d.get("games_played", 0)
        movie.visible_score = d.get("visible_score", 0.0)
        return movie
