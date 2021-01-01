from flask import Flask, render_template, url_for
import pandas as pd
pd.set_option('display.max_columns', 25)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.prediction_algorithms import knns
from surprise.model_selection import train_test_split, KFold, GridSearchCV
from surprise import accuracy
from surprise import dump
import os
import random
from collections import defaultdict
from time import time
from recommender import createbestalgorithm


app = Flask(__name__)


#loads the csv files as dataframes
ratings = pd.read_csv('ratings.csv')
# taking 10% of the ratings and books dating frames
smallerratings = ratings.sample(frac = 0.1, replace = True, random_state = 1)
books = pd.read_csv('books.csv')
smallerbooks = books.sample(frac = 0.1, replace = True, random_state = 1)

  

# define reader
reader = Reader(rating_scale=(1, 5))

# load dataframe into correct format for surprise library
data = Dataset.load_from_df(smallerratings[['user_id', 'book_id', 'rating']], reader)
# splitting the data set so that 20% of it is a test set, whilst the rest of the data is the training set 
trainset, testset = train_test_split(data, test_size=0.2, random_state=0)
# creating an SVD object for the algorithm
svd = SVD()



#fit and test algorithm
predictions = svd.fit(trainset).test(testset)






# route to the homepage
@app.route('/')
@app.route('/home')
def index():
    closeness_of_fit = accuracy.rmse(predictions)
    return render_template('index.html', variable = closeness_of_fit )   

@app.route('/next')
def next():
    return render_template('next.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

if __name__ == "__main__":
    app.run(debug=True) 