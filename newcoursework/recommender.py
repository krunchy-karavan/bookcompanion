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
# measuring how accurate  predictions is
closeness_of_fit = accuracy.rmse(predictions)
print(closeness_of_fit)

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

def makepredictions(ratings,smallerratings,smallerbooks,newfile):
    # creates a new user id so that the user's rating can be added to the test data to make a prediction
    new_user_id = ratings.user_id.nunique()+1
    # an array to store all the ratings the user makes
    ratingslist = []
    
    # allows the user to be able to determine how mant books they want to rate
    num_ratings = int(input('How many books would you like to rate. The more books you rate, the more accurate your predictions will be'))
    while num_ratings > 0:
        # pulls a random_book out of the smallerbooks dataframe
        random_book = smallerbooks.sample(1, random_state = None)
        # outputs the title and author of the random_book
        print(random_book[['title','authors']].values)
        # Takes the user's rating for the book from 1-5 as well as taking an N incase they haven't read the book
        user_rating = input('Rate this book from 1-5. If you have not read this book, enter N')
        if user_rating == 'N':
            pass
        # validates if the input is between 1-5
        elif 49 <= ord(user_rating) <= 53:
            # creates a dictionary so that the book rating is in the same format as all the testset ratings
            random_book_rating = {'user_id':new_user_id, 'book_id':smallerbooks['book_id'].values[0], 'rating':user_rating}
            # adds this record to the ratings list array
            ratingslist.append(random_book_rating)
            # this along with the loop ensures that ratingslist has the same no. of ratings as num_ratings
            #without any blanks
            num_ratings -= 1
        else:
            print("This is an invalid input")
            user_rating = input('Rate this book from 1-5. If you have not read this book, enter N')
            

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
        title = books.loc[books['book_id'] == int(rec[0])]['title']
        recommended_title = 'Recommendation # ', idx+1, ': ', title, '\n'
        recommended_titles_list.append(recommended_title)
        num_rec-= 1
        if num_rec == 0:
            break
    print(recommended_titles_list)
    
newfile = createbestalgorithm(data)
makepredictions(ratings,smallerratings,smallerbooks,newfile)