# MovieRecommenderApp
Here is a little project i had to do for University.The project is a movie recommender app made using webscraping from tmdb,a pretrained ML model and a frontend maked using flask.
The program works this way: first the pretrained ML model takes the Description and Keywords collumn fromm the dataframe and embedd them into one long string(this actions is made for every movie in the dataset), then the same is done for the user input and after that we use cosine similarity in order to  compare the user input with every movie description and keywords in the dataframe.The top 10 most similar movies will be sent back to the front end.
In order to start the program: run front.py and access the link that is shown in the terminal and have fun.
