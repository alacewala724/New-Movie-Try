# ranking.py

class RankingEngine:
    DEFAULT_ELO = 1400
    PROVISIONAL_K = 64
    STANDARD_K = 32
    MIN_K = 16

    def __init__(self):
        pass

    def expected_score(self, elo_a, elo_b):
        return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    
    def get_k_factor(self, movie):
        if movie.games_played < 5:
            return self.PROVISIONAL_K
        elif movie.games_played < 20:
            return self.STANDARD_K
        else:
            return self.MIN_K

    def update_ratings(self, movie_a, movie_b, outcome):
        """
        Update Elo ratings for two movies.
        outcome: True if movie_a wins; False if movie_b wins.
        """
        expected_a = self.expected_score(movie_a.elo, movie_b.elo)
        expected_b = 1 - expected_a
        k_a = self.get_k_factor(movie_a)
        k_b = self.get_k_factor(movie_b)
        score_a = 1 if outcome else 0
        score_b = 0 if outcome else 1

        movie_a.elo += k_a * (score_a - expected_a)
        movie_b.elo += k_b * (score_b - expected_b)

        movie_a.games_played += 1
        movie_b.games_played += 1
        if outcome:
            movie_a.wins += 1
            movie_b.losses += 1
        else:
            movie_a.losses += 1
            movie_b.wins += 1
        
        movie_a.visible_score = self.calculate_visible_score(movie_a)
        movie_b.visible_score = self.calculate_visible_score(movie_b)

    def calculate_visible_score(self, movie):
        # Base visible score per rating category.
        base_scores = {"good": 8.5, "okay": 6.0, "bad": 3.0}
        base = base_scores.get(movie.rating, 6.0)
        adjustment = (movie.elo - self.DEFAULT_ELO) / 400  # A rough adjustment factor
        visible = base + adjustment

        # Clamp the visible score to a reasonable range.
        if movie.rating == "good":
            visible = max(8.0, min(9.9, visible))
        elif movie.rating == "okay":
            visible = max(5.0, min(8.0, visible))
        else:
            visible = max(1.0, min(5.0, visible))
        return round(visible, 1)
