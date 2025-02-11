#cd ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from models import Movie
from ranking import RankingEngine
from persistence import PersistenceManager
from api_client import TMDBClient

class MovieRankerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Beli for Movies")
        self.root.geometry("800x600")

        # Instantiate modules
        self.persistence = PersistenceManager()
        self.ranking_engine = RankingEngine()
        self.tmdb_client = TMDBClient()

        # Load movies from disk.
        self.movies = self.persistence.load_movies()
        self.current_movie = None
        self.current_comparison = None

        self.setup_ui()

    def setup_ui(self):
        # Using a Notebook (tabbed interface) to separate functions.
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab: Add / Search Movie
        self.frame_add = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_add, text="Add Movie")
        self.setup_add_frame()

        # Tab: Rate New Movie
        self.frame_rate = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_rate, text="Rate Movie")
        self.setup_rate_frame()

        # Tab: Compare Movies
        self.frame_compare = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_compare, text="Compare Movies")
        self.setup_compare_frame()

        # Tab: Rankings
        self.frame_rankings = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_rankings, text="Rankings")
        self.setup_rankings_frame()

        self.refresh_rankings_list()
        self.notebook.select(self.frame_rankings)

    def setup_add_frame(self):
        lbl = ttk.Label(self.frame_add, text="Search for a movie:")
        lbl.pack(pady=10)

        self.entry_search = ttk.Entry(self.frame_add, width=50)
        self.entry_search.pack(pady=5)
        self.entry_search.bind("<KeyRelease>", self.on_search_key_release)

        self.listbox_suggestions = tk.Listbox(self.frame_add, height=5)
        self.listbox_suggestions.pack(pady=5, fill=tk.X)
        self.listbox_suggestions.bind("<Double-Button-1>", self.on_suggestion_double_click)

        btn_add = ttk.Button(self.frame_add, text="Add Movie", command=self.add_movie)
        btn_add.pack(pady=10)

        btn_delete = ttk.Button(self.frame_add, text="Delete All Movies", command=self.delete_all_movies)
        btn_delete.pack(pady=5)

    def setup_rate_frame(self):
        self.lbl_rate = ttk.Label(self.frame_rate, text="How would you rate this movie?")
        self.lbl_rate.pack(pady=20)

        btn_frame = ttk.Frame(self.frame_rate)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Good 👍", command=lambda: self.set_movie_rating("good")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Okay 👌", command=lambda: self.set_movie_rating("okay")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Bad 👎", command=lambda: self.set_movie_rating("bad")).pack(side=tk.LEFT, padx=5)

    def setup_compare_frame(self):
        self.lbl_compare = ttk.Label(self.frame_compare, text="Select the better movie:")
        self.lbl_compare.pack(pady=20)

        self.btn_movie_a = ttk.Button(self.frame_compare, text="Movie A", command=lambda: self.handle_comparison(True))
        self.btn_movie_a.pack(pady=5, fill=tk.X, padx=20)

        self.btn_movie_b = ttk.Button(self.frame_compare, text="Movie B", command=lambda: self.handle_comparison(False))
        self.btn_movie_b.pack(pady=5, fill=tk.X, padx=20)

    def setup_rankings_frame(self):
        self.listbox_rankings = tk.Listbox(self.frame_rankings, font=("Courier New", 12))
        self.listbox_rankings.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_refresh = ttk.Button(self.frame_rankings, text="Refresh Rankings", command=self.refresh_rankings_list)
        btn_refresh.pack(pady=5)

    # ---------------------------
    # Search and Add Functions
    # ---------------------------
    def on_search_key_release(self, event):
        query = self.entry_search.get().strip()
        if len(query) < 2:
            self.listbox_suggestions.delete(0, tk.END)
            return
        # Perform the API search in a separate thread.
        threading.Thread(target=self.search_movies, args=(query,), daemon=True).start()

    def search_movies(self, query):
        results = self.tmdb_client.search_movies(query)
        # Update suggestions in the main thread.
        self.root.after(0, self.update_suggestions, results)

    def update_suggestions(self, results):
        self.listbox_suggestions.delete(0, tk.END)
        self.suggestions = results
        for movie in results:
            title = movie.get("title", "Unknown Title")
            year = movie.get("release_date", "")[:4]
            display = f"{title} ({year})" if year else title
            self.listbox_suggestions.insert(tk.END, display)

    def on_suggestion_double_click(self, event):
        self.add_movie()

    def add_movie(self):
        selected_indices = self.listbox_suggestions.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Please select a movie from suggestions.")
            return
        index = selected_indices[0]
        movie_data = self.suggestions[index]
        title = movie_data.get("title")
        self.current_movie = Movie(title)
        self.lbl_rate.config(text=f"How would you rate '{title}'?")
        self.notebook.select(self.frame_rate)

    def delete_all_movies(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all movies? This cannot be undone."):
            if self.persistence.delete_movies():
                self.movies = []
                self.refresh_rankings_list()
                messagebox.showinfo("Success", "All movies have been deleted.")
            else:
                messagebox.showerror("Error", "Failed to delete movies.")
    # ---------------------------
    # Rating Functions
    # ---------------------------
    def set_movie_rating(self, rating):
        if not self.current_movie:
            return
        self.current_movie.rating = rating
        # Set base Elo based on rating.
        base_elo = {"good": 1500, "okay": 1400, "bad": 1300}.get(rating, 1400)
        self.current_movie.elo = base_elo
        # Calculate the initial visible score.
        self.current_movie.visible_score = self.ranking_engine.calculate_visible_score(self.current_movie)
        self.movies.append(self.current_movie)
        self.persistence.save_movies(self.movies)
        self.refresh_rankings_list()
        # If there is at least one other movie, set up a comparison.
        if len(self.movies) > 1:
            self.current_comparison = self.select_comparison(self.current_movie)
            if self.current_comparison:
                self.setup_comparison_ui()
                self.notebook.select(self.frame_compare)
            else:
                messagebox.showinfo("Info", "No suitable movie for comparison.")
                self.notebook.select(self.frame_rankings)
        else:
            self.notebook.select(self.frame_rankings)
        self.current_movie = None

    # ---------------------------
    # Comparison Functions
    # ---------------------------
    def select_comparison(self, new_movie):
        # Select a candidate movie (other than new_movie) based on closest Elo.
        candidates = [m for m in self.movies if m.title != new_movie.title]
        if not candidates:
            return None
        candidates.sort(key=lambda m: abs(m.elo - new_movie.elo))
        return candidates[0]

    def setup_comparison_ui(self):
        # Assume the new movie is the last added.
        new_movie = self.movies[-1]
        self.btn_movie_a.config(text=new_movie.title)
        self.btn_movie_b.config(text=self.current_comparison.title)

    def handle_comparison(self, outcome):
        new_movie = self.movies[-1]
        candidate = self.current_comparison
        # Outcome True means the new movie wins.
        if outcome:
            winner, loser = new_movie, candidate
        else:
            winner, loser = candidate, new_movie
        self.ranking_engine.update_ratings(winner, loser, outcome)
        self.persistence.save_movies(self.movies)
        self.refresh_rankings_list()
        messagebox.showinfo("Comparison", f"'{winner.title}' wins the comparison!")
        self.notebook.select(self.frame_rankings)

    # ---------------------------
    # Rankings Functions
    # ---------------------------
    def refresh_rankings_list(self):
        self.listbox_rankings.delete(0, tk.END)
        sorted_movies = sorted(self.movies, key=lambda m: m.visible_score, reverse=True)
        for m in sorted_movies:
            display = f"{m.title:<30} Score: {m.visible_score:>4}  Elo: {int(m.elo)}"
            self.listbox_rankings.insert(tk.END, display)

def main():
    root = tk.Tk()
    app = MovieRankerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
