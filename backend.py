import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self):
        print("🔄 Loading backend data...")
        try:
            with open('movies_data.pkl', 'rb') as f:
                self.df = pickle.load(f)
            with open('movies_embeddings.pkl', 'rb') as f:
                self.embeddings = pickle.load(f)
            
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # --- PRE-PROCESARE DATE ---
            # 1. Curățăm ANUL
            self.df['release_date'] = pd.to_datetime(self.df['release_date'], errors='coerce')
            self.df['year_num'] = self.df['release_date'].dt.year.fillna(0).astype(int)
            
            # 2. Curățăm NOTA (convertim la numere)
            self.df['vote_average'] = pd.to_numeric(self.df['vote_average'], errors='coerce').fillna(0)
            
            print("✅ Backend ready!")
            self.is_ready = True
        except Exception as e:
            print(f"❌ Error loading backend: {e}")
            self.is_ready = False

    # AICI AM ADĂUGAT min_rating (Al 4-lea parametru)
    def get_recommendations(self, user_text, genre_filter="All", year_filter="Anytime", min_rating=0.0):
        if not self.is_ready:
            return []

        # 1. Calculăm scorul AI
        embedding = self.model.encode([user_text])
        similarities = cosine_similarity(embedding, self.embeddings)[0]
        
        working_df = self.df.copy()
        working_df['similarity_score'] = similarities

        # 2. APLICĂM FILTRELE
        
        # A. Filtru Gen
        if genre_filter != "All":
            working_df = working_df[working_df['genres'].str.contains(genre_filter, case=False, na=False)]

        # B. Filtru An
        if year_filter != "Anytime":
            try:
                start_year = int(year_filter.replace("s", ""))
                end_year = start_year + 9
                working_df = working_df[
                    (working_df['year_num'] >= start_year) & 
                    (working_df['year_num'] <= end_year)
                ]
            except: pass

        # C. Filtru RATING (Logica nouă)
        if min_rating > 0:
            working_df = working_df[working_df['vote_average'] >= min_rating]

        # 3. Sortăm și luăm top 10
        results_df = working_df.sort_values(by='similarity_score', ascending=False).head(10)

        # 4. Formatăm
        results = []
        for _, row in results_df.iterrows():
            title = str(row['title']).replace(',', '')
            genres = str(row['genres']).replace(',', '|')
            date = str(row['release_date']).split()[0] if pd.notnull(row['release_date']) else "N/A"
            rating = str(row['vote_average'])
            
            results.append(f"{title}, {genres}, {date}, {rating}")
            
        return results

# --- INSTANȚIERE ---
engine = MovieRecommender()


# --- FIXAREA ERORII TALE AICI JOS ---
# Acum funcția acceptă 4 argumente!
def get_recommendations(text, genre="All", year="Anytime", rating=0.0):
    return engine.get_recommendations(text, genre, year, rating)