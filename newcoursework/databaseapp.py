from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
from form import CategorySelect, PastebinEntry,Loginform
import random

app = Flask(__name__)
app.static_folder = 'static'

def getfetchdata(data):
        category = 'category'
        r = 'sort_by_rating'
        if category in data:
          category = data['category']
          # executes an SQL statement to select book details based on category
          result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ")
          fetchdata = db.engine.execute(result, category=category)
        elif r in data:
          result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ORDER BY average_rating DESC")
          fetchdata = db.engine.execute(result, category=category)
        return fetchdata

def testgetfetchdata(data,var):
  if var == 1:
    category = 'category'
    r = 'sort_by_rating'
    if category in data:
      category = data['category']
      # executes an SQL statement to select book details based on category
      result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ")
      fetchdata = db.engine.execute(result, category=category)
    elif r in data:
      result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ORDER BY average_rating DESC")
      fetchdata = db.engine.execute(result, category=category)
  else:
    selectall = "SELECT authors, title, image_url , book_id FROM books LIMIT 10"
    allbooks = text(selectall)
    fetchdata = db.engine.execute(allbooks).fetchall()
  return fetchdata

def searchfiltering(fetchdata,filterstring):
  filteredfetchdata = list(filter(lambda x: filterstring in x[1], fetchdata))
  return filteredfetchdata


hostname="localhost"
dbname="library"
uname="root"
pwd="kunsa3002"

# Create dataframe

df = pd.read_csv('book_tags.csv')

# Create SQLAlchemy engine to connect to MySQL Database
db = create_engine("mysql://{user}:{pw}@{host}/{db}"
    .format(host=hostname, db=dbname, user=uname, pw=pwd))

# Convert dataframe to sql table    
                           
#df.to_sql('book_tags', db, index=False, if_exists = 'replace')
#result = db.engine.execute("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) ")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kunsa3002'
app.config['MYSQL_DB'] = 'library'

mysql = MySQL(app)
@app.route('/', methods = ['GET', 'POST'])
def loginpage():
  login= Loginform()
  return render_template('login.html', loginform = login)


@app.route('/browse', methods = ['GET','POST'])
def browse():
    # creates the connection object, which allows us to write SQL queries in the code
    book_tags_df = pd.read_csv('book_tags.csv')
    cur = mysql.connection.cursor()

    cur.execute("SELECT tag_name FROM tags ")
    category_names = cur.fetchall()
    # creates a form object of the category select form
    category_select_form = CategorySelect(taglist= category_names)
    stufftobefiltered = request.args.get('jsdata')
    fetchdata = 21
    var = 1

      # if statement to make sure the data is entered and validated
    if category_select_form.is_submitted():
      var = 1
      # pulls the information submitted from the form into a dictionary
      data = request.form
      # gets the category from the dictionary data
    else:
      var = 0
      data = None
    print('var = ', var)
    fetchdata = testgetfetchdata(data,var)
    print(var)
      
   

    # closes connection object
    cur.close()
    

    # passes fetchdata to the html page so the data can be outputed on the website
    return render_template('browse.html', data = fetchdata, form=category_select_form)


@app.route('/book', methods = ['GET','POST'])
def books():
  if request.method == 'POST':
    # get the data from the form as a dictionary
    formdata = request.form
    # get the value of the book_id from the dictionary
    book_id = formdata['passingdata']
    # SQL query for the details of the book with that book_id by passing it as a parameter
    bookstats = ['Title', 'Authors', 'Year Published', 'Avg Rating', 'ISBN', 'ISBN13', 'Image_url']
    bookquery = text(" SELECT original_title, authors, original_publication_year,average_rating, isbn, isbn13, image_url FROM books WHERE books.book_id = :book_id")
    result = db.engine.execute(bookquery,book_id=book_id).fetchall()
    result = result[0]

    dictionary = dict(zip(bookstats,result))
    print(dictionary)
  return render_template('book.html', result=dictionary)


if __name__ == "__main__":  
  app.config['SECRET_KEY'] = '12111111'
  app.run(debug=True)