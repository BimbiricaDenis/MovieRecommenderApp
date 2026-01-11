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
            
            # Preprocessing DataFrame
            # 1. Firt, convert the YEAR column to numeric
            self.df['Year'] = pd.to_datetime(self.df['Year'], errors='coerce')
            self.df['year_num'] = self.df['Year'].dt.year.fillna(0).astype(int)
            
            # 2. Convert the RATING column to numeric, handling errors
            self.df['Rating'] = pd.to_numeric(self.df['Rating'], errors='coerce').fillna(0)

            print("✅ Backend ready!")
            self.is_ready = True
        except Exception as e:
            print(f"❌ Error loading backend: {e}")
            self.is_ready = False

    def get_recommendations(self, user_text, genre_filter="All", year_filter="Anytime", min_rating=0.0):
        if not self.is_ready:
            return []
        
        embedding = self.model.encode([user_text])
        similarities = cosine_similarity(embedding, self.embeddings)[0]
        
        working_df = self.df.copy()
        working_df['similarity_score'] = similarities

        # Aplying Filters
        
        # A. Filtre the GENRE
        if genre_filter != "All":
            working_df = working_df[working_df['Genre'].str.contains(genre_filter, case=False, na=False)]

        # B. Filtre the YEAR
        if year_filter != "Anytime":
            try:
                start_year = int(year_filter.replace("s", ""))
                end_year = start_year + 9
                working_df = working_df[
                    (working_df['year_num'] >= start_year) & 
                    (working_df['year_num'] <= end_year)
                ]
            except: pass

        # C. Filtre the RATING
        if min_rating > 0:
            working_df = working_df[working_df['Rating'] >= min_rating]

        # 3. We sort and take top 10
        results_df = working_df.sort_values(by='similarity_score', ascending=False).head(10)

        # 4. Formatting the results
        results = []
        for _, row in results_df.iterrows():
            title = str(row['Title']).replace(',', '')
            genres = str(row['Genre']).replace(',', '|')
            date = str(row['Year']).split()[0] if pd.notnull(row['Year']) else "N/A"
            rating = str(row['Rating'])
            
            results.append(f"{title}, {genres}, {date}, {rating}")
            
        return results

engine = MovieRecommender()

def get_recommendations(text, genre="All", year="Anytime", rating=0.0):
    return engine.get_recommendations(text, genre, year, rating)