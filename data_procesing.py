import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
import os

#A function that processes the movie dataset and creates embeddings,saving them in pickle files.
def create_embeddings():
    try:
        movies=pd.read_csv('tmdb_5000_movies.csv')
    except FileNotFoundError:
        print("The file 'tmdb_5000_movies.csv' was not found.")
        return
    
    print(movies.shape)
    model=SentenceTransformer('all-MiniLM-L6-v2')
    movies['Description']=movies['Description'].astype(str)
    movies['Keywords']=movies['Keywords'].astype(str)
    movies['combined_text']=movies['Description']+'. '+movies['Keywords']
    embeddings = model.encode(movies['combined_text'].tolist(), show_progress_bar=True)

    with open('movies_data4.pkl', 'wb') as f:
        pickle.dump(movies, f)

    with open('movies_embeddings4.pkl', 'wb') as f:
        pickle.dump(embeddings, f)

    print("Data processing and embedding creation completed successfully.")

if __name__ == "__main__":
    create_embeddings()
