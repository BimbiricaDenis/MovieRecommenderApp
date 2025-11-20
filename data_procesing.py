import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
import os

#A function that processes the movie dataset and creates embeddings,saving them in pickle files.
def create_embeddings():
    try:
        movies=pd.read_csv('TMDB_movie_dataset_v11.csv')
    except FileNotFoundError:
        print("The file 'TMDB_movie_dataset_v11.csv' was not found.")
        return
    
    movies=movies[['id','title','vote_average','vote_count','release_date','overview','popularity','genres','keywords']]
    print(movies.shape())
    movies=movies.dropna(axis=0,how='any',inplace=False,ignore_index=True)
    print(movies.shape())
    model=SentenceTransformer('all-MiniLM-L6-v2')
    movies['title']=movies['title'].astype(str)
    movies['overview']=movies['overview'].astype(str)
    movies['keywords']=movies['keywords'].astype(str)
    movies['combined_text']=movies['title']+'. '+movies['overview']+'. '+movies['keywords']
    embeddings = model.encode(movies['combined_text'].tolist(), show_progress_bar=True)

    with open('movies_data.pkl', 'wb') as f:
        pickle.dump(movies, f)

    with open('movies_embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings, f)

    print("Data processing and embedding creation completed successfully.")

if __name__ == "__main__":
    create_embeddings()
