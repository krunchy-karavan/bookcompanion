from flask import Flask, render_template, url_for, request
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
from flask_wtf import FlaskForm, Form
from form import recommender_inputs,Signupform, BaseFormTemplate





app = Flask(__name__)
app.static_folder = 'static'

from wtforms import StringField, PasswordField, SubmitField



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

def createbestalgorithm(data): 
    # creating a new validation set to help fine-tune the parameters of the 
    raw_ratings = data.raw_ratings

    # shuffle ratings
    random.shuffle(raw_ratings)

    # A = 80% of the data, B = 20% of the data
    threshold = int(.8 * len(raw_ratings))
    A_raw_ratings = raw_ratings[:threshold]
    B_raw_ratings = raw_ratings[threshold:]

    data.raw_ratings = A_raw_ratings  # data is now the set A
    t = time()
    #define parameter grid and fit gridsearch on set A data
    # n_epochs is the no. of times it algorithm is performed on the entire training data
    #lr_all is the learning rate of the parameters( which is the amount by which they'll change each time the model goe
    # goes through the training data)
    param_grid = {'n_epochs': [5,10], 'lr_all': [0.001, 0.01]}
    # function which iterates through multiple SVD algorithms, each with slightly different parameters
    # as the algorithms are performed, optimizing to a more accurate algorithm in the given time 
    grid_search = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3)
    grid_search.fit(data)

    # gets the best algorithm out of all the svd algorithms perforemd by GridsearchCV
    best_algorithm = grid_search.best_estimator['rmse']


    # retrain on the whole set A
    trainset = data.build_full_trainset()
    best_algorithm.fit(trainset)

    # test the best_svd algorithm on set B
    testset = data.construct_testset(B_raw_ratings)   
    newpredictions = best_algorithm.test(testset)
    # print the rmse of this new algorithm
    goodness_of_fit = accuracy.rmse(newpredictions)
    print(goodness_of_fit)

    # give file a name
    newfile= os.path.expanduser('~/somewhere')
    # save best model
    dump.dump(newfile, algo=best_algorithm)
    # load saved model
    return newfile




def makepredictions_generate_rating_books(num_ratings, smallerbooks):
    # create an array of books for the user to rate
    random_book_list = []
    # iterates through to create an intiial list of books to rate
    while num_ratings > 0:
        random_book = smallerbooks.sample(1, random_state = None)
        print(random_book.info)
        random_book_details = random_book[['book_id','title','authors']].values.tolist()
        random_book_list.append(random_book_details)
        num_ratings -= 1
    return random_book_list

num_ratings = 5

def makepredictions_output(newfile,ratingslist,ratings):
    new_user_id = ratings.user_id.nunique()+1
    # turns the ratinglist into the same format as smallerratings        
    df = pd.DataFrame(ratingslist)
    # adds the user ratings in ratinglist to the smallerratings database to make a new dataset
    new_smaller_ratings = smallerratings.append(df,ignore_index = True)
    reader = Reader(rating_scale=(1,5))
    # creates a new matrix using the user_id, book_id, and rating from the new_smaller_ratings dataset
    new_data = Dataset.load_from_df(new_smaller_ratings[['user_id', 'book_id', 'rating']],reader)
    # loads the best algorithm 
    _, best_svd = dump.load(newfile)
    # applies it to the dataset
    best_svd.fit(new_data.build_full_trainset())

    # creates the predicted ratings for the user for all the books
    predictionlist = []
    for book_id in new_smaller_ratings['book_id'].unique():
        predictionlist.append((book_id,best_svd.predict(new_user_id, book_id)[3]))
        # no of recommendations that the user wants
    num_rec = 5
    # ranks the predictions from highest rating to lowest
    ranked_predictions = sorted(predictionlist, key=lambda x:x[1], reverse=True)
    
    # list of recommended titles that I can return as an array, I'll then be able to output them individually
    # in the html 
    recommended_titles_list = []
    #iterates through the loop to output the top n recommendations
    for idx, rec in enumerate(ranked_predictions):
        # gets the title of each book
        title = books.loc[books['book_id'] == int(rec[0])]['title']
        # creates a string of Recommendation no. [title] for each book
        recommended_title = 'Recommendation # ', idx+1, ': ', title, '\n'
        # adds each recommended title to an array
        recommended_titles_list.append(recommended_title)
        num_rec-= 1
        if num_rec == 0:
            break
    return recommended_titles_list


newfile = createbestalgorithm(data)



# route to the homepage
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def index():
    # gets the list of random books the user needs to rate
    ratingbooks = makepredictions_generate_rating_books(num_ratings, smallerbooks)
    print(ratingbooks)

    # returns just the title of each book and stores it in a list
    '''ratingbooktitlelist = []
    for i in range(0,len(ratingbooks)):
        x = ratingbooks[i][0][1]
        ratingbooktitlelist.append(x)'''
    
    ratingbookdict = {}
    for i in range(0, len(ratingbooks)):
        x = str(ratingbooks[i][0][0])
        y = ratingbooks[i][0][1]
        ratingbookdict[x] = y
    print(ratingbookdict)

    
    
    
    # creates a class for the object of the ratingform
    class RatingForm(BaseFormTemplate):
        pass
    # create a submit button for the form
    RatingForm.submit = SubmitField('submit')
    # create a text field for each title in the ratingbooktitlelist, so the user can input their rating
    for key in ratingbookdict:
        setattr(RatingForm, key, StringField(ratingbookdict[key]))
    # create an object of the form class to create the form for the HTML
    form = RatingForm()
    # checks if the form has been submitted
    if form.is_submitted():
        # returns a dictionary with the keys being the variable names of the form's fields, and the values being the user input
        # for the fields
        result = request.form.to_dict()
        result.pop('csrf_token')
        result.pop('submit')
        new_user_id = ratings.user_id.nunique()+1
        i = 0
        ratingslist = []
        for key in result:
            user_rating = { 'user_id': new_user_id,  'book_id': int(key),'rating':result[key]}
            ratingslist.append(user_rating)

        print(ratingslist)        
        recommended_title_list = makepredictions_output(newfile, ratingslist,ratings)
            
        return render_template('result.html', result = result)

        

    return render_template('index.html', form = form, variable = ratingbooks)   

@app.route('/next')
def next():
    return render_template('next.html')
@app.route('/discover')
def discover(): 
    return render_template('discover.html')

if __name__ == "__main__":
    app.config['SECRET_KEY'] = '12345'
    app.run(debug=True) 