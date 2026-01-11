import customtkinter as ctk
import os
import requests
import threading
from PIL import Image, ImageTk
from io import BytesIO

# --- IMPORT BACKEND ---
try:
    import Proiect.backend as backend
except ImportError:
    print("⚠️ EROARE: Fișierul 'backend.py' nu a fost găsit!")

# --- API KEY TMDB (for the posters) ---
TMDB_API_KEY = "873e9f0f953fa2189413de6263c341ec" 

script_directory = os.path.dirname(os.path.abspath("MovieRecommenderApp"))

class MovieAppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setting Window Properties
        self.title("AI Movie Recommender")

        icon_path= os.path.join("MovieRecommenderApp", "icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error: Could not load window icon from {icon_path}: {e}")
        
        # Centering the Window
        app_width = 1100
        app_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - app_width) // 2
        y = (screen_height - app_height) // 2
        self.geometry(f"{app_width}x{app_height}+{x}+{y}")
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue") 
        self.configure(fg_color="#1a1a1a") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) 

        self.load_icons()
        self.build_ui()

    def load_icons(self):
        self.genre_icon = None
        self.year_icon = None
        self.rating_icon = None
        try:
            self.genre_icon = ctk.CTkImage(Image.open(os.path.join(script_directory, "icon_genre.png")), size=(20, 20))
            self.year_icon = ctk.CTkImage(Image.open(os.path.join(script_directory, "period.png")), size=(22, 22))
            self.rating_icon = ctk.CTkImage(Image.open(os.path.join(script_directory, "rating.png")), size=(17, 17))
        except: pass

    def build_ui(self):
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(30, 20))
        
        ctk.CTkLabel(header_frame, text="Find Your ", font=("Roboto", 32, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header_frame, text="Perfect Movie", font=("Roboto", 32, "bold"), text_color="#E91E63").pack(side="left")

        # --- SEARCH BAR ---
        self.search_entry = ctk.CTkEntry(self, 
                                         placeholder_text="Describe the plot (e.g., 'time travel paradox', 'love in paris')...", 
                                         width=700, height=50, 
                                         font=("Arial", 16), 
                                         corner_radius=25, 
                                         fg_color="#2b2b2b", border_color="#333", border_width=2)
        self.search_entry.grid(row=1, column=0, pady=10)

        # --- FILTERS ---
        filters_container = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        filters_container.grid(row=2, column=0, pady=10, padx=100, sticky="ew")
        filters_container.grid_columnconfigure((0, 1, 2), weight=1)

        # A. Genre
        box_genre = ctk.CTkFrame(filters_container, fg_color="transparent")
        box_genre.grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkLabel(box_genre, text="Genre", font=ctk.CTkFont(weight="bold"), image=self.genre_icon, compound="left").pack(anchor="w", pady=(0, 10))
        
        self.genre_var = ctk.StringVar(value="All")
        ctk.CTkComboBox(box_genre, values=["All", "Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance"], 
                        variable=self.genre_var, width=200, height=35, 
                        fg_color="#343638", button_color="#E91E63").pack()

        # B. Period
        box_year = ctk.CTkFrame(filters_container, fg_color="transparent")
        box_year.grid(row=0, column=1, padx=20, pady=20)
        ctk.CTkLabel(box_year, text="Period", font=ctk.CTkFont(weight="bold"), image=self.year_icon, compound="left").pack(anchor="w", pady=(0, 10))
        
        self.year_var = ctk.StringVar(value="Anytime")
        decades = ["Anytime"] + [f"{year}s" for year in range(2020, 1949, -10)]
        ctk.CTkComboBox(box_year, values=decades, variable=self.year_var, 
                        width=200, height=35, fg_color="#343638", button_color="#E91E63").pack()

        # C. Rating
        box_rating = ctk.CTkFrame(filters_container, fg_color="transparent")
        box_rating.grid(row=0, column=2, padx=20, pady=20)
        ctk.CTkLabel(box_rating, text="Minimum Rating", font=ctk.CTkFont(weight="bold"), image=self.rating_icon, compound="left").pack(anchor="w", pady=(0, 10))
        
        self.rating_var = ctk.DoubleVar(value=6.0)
        self.rating_slider = ctk.CTkSlider(box_rating, from_=0, to=9, number_of_steps=9, variable=self.rating_var, 
                                           command=self.update_rating_label, width=200, button_color="#E91E63", progress_color="#E91E63")
        self.rating_slider.pack(pady=(5,0))
        
        self.rating_label = ctk.CTkLabel(box_rating, text="6.0+", font=ctk.CTkFont(size=12), text_color="#E91E63")
        self.rating_label.pack()

        # --- BUTTON ---
        self.search_btn = ctk.CTkButton(self, text="🔍 Search Recommendations", width=300, height=55,
                                        font=("Arial", 18, "bold"), corner_radius=25, fg_color="#E91E63", hover_color="#C2185B",
                                        command=self.start_search_thread)
        self.search_btn.grid(row=3, column=0, pady=20)
        
        # --- RESULTS AREA ---
        self.results_frame = ctk.CTkScrollableFrame(self, height=300, fg_color="#242424", border_color="#333", border_width=1)
        self.results_frame.grid(row=4, column=0, sticky="nsew", padx=100, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.results_frame, text="Your AI recommendations will appear here...", text_color="gray", font=("Arial", 14, "italic"))
        self.status_label.pack(pady=50)

    def update_rating_label(self, value):
        self.rating_label.configure(text=f"{value:.1f}+")

    def get_poster_url(self, title):
        if "PUNE_AICI" in TMDB_API_KEY: return "N/A"
        try:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
            res = requests.get(url, timeout=2).json()
            if res.get('results'): 
                path = res['results'][0].get('poster_path')
                if path: return f"https://image.tmdb.org/t/p/w200{path}"
        except: pass
        return "N/A"

    # --- SEARCH LOGIC ---
    def start_search_thread(self):
        threading.Thread(target=self.run_search_logic, daemon=True).start()

    def run_search_logic(self):
        # 1. Collect data from UI
        text_input = self.search_entry.get()
        genre_filter = self.genre_var.get()
        year_filter = self.year_var.get()
        rating_filter = self.rating_var.get() 
        
        if not text_input.strip(): return

        # UI Update
        self.clear_results()
        self.status_label.configure(text=f"🧠 AI searching... Filters: {genre_filter}, {year_filter}, {rating_filter}+ ⭐")
        self.status_label.pack(pady=50)

        try:
            results = backend.get_recommendations(text_input, genre_filter, year_filter, rating_filter)
            
            self.status_label.pack_forget()

            if not results:
                self.status_label.configure(text="No movies found with these strict filters.")
                self.status_label.pack(pady=50)
                return

            for movie_str in results:
                parts = movie_str.split(',')
                if len(parts) >= 4:
                    title = parts[0].strip()
                    genre = parts[1].strip()
                    date = parts[2].strip()
                    rating_str = parts[3].strip()

                    poster = self.get_poster_url(title)
                    self.create_movie_card(title, genre, date, rating_str, poster)

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            self.status_label.pack()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.status_label = ctk.CTkLabel(self.results_frame, text="", text_color="gray")

    def create_movie_card(self, title, genre, date, rating, poster_url):
        card = ctk.CTkFrame(self.results_frame, fg_color="#2b2b2b", corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        # Imagine
        if poster_url != "N/A":
            try:
                data = requests.get(poster_url, timeout=2).content
                img = ctk.CTkImage(Image.open(BytesIO(data)), size=(80, 120))
                ctk.CTkLabel(card, text="", image=img).grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            except: 
                ctk.CTkLabel(card, text="No\nImg", width=80, height=120, fg_color="#444").grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        else:
            ctk.CTkLabel(card, text="No\nImg", width=80, height=120, fg_color="#444").grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Text
        ctk.CTkLabel(card, text=title, font=("Arial", 18, "bold"), anchor="w").grid(row=0, column=1, sticky="sw", padx=10)
        ctk.CTkLabel(card, text=f"{genre} | {date}", text_color="gray", anchor="w").grid(row=1, column=1, sticky="nw", padx=10)
        
        # Rating
        try:
            score = float(rating)
            col = "#4CAF50" if score >= 7.5 else "#FFC107" if score >= 5 else "#F44336"
        except: col = "white"
        ctk.CTkLabel(card, text=f"⭐ {rating}", font=("Arial", 20, "bold"), text_color=col).grid(row=0, column=2, rowspan=2, padx=20)

if __name__ == "__main__":
    app = MovieAppUI()
    app.mainloop()