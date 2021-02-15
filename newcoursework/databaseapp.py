from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
from form import CategorySelect, PastebinEntry
import random

app = Flask(__name__)
app.static_folder = 'static'

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
@app.route('/browse', methods = ['GET','POST'])
@app.route('/', methods = ['GET', 'POST'])
def browse():
    # creates the connection object, which allows us to write SQL queries in the code
    book_tags_df = pd.read_csv('book_tags.csv')
    cur = mysql.connection.cursor()

    cur.execute("SELECT tag_name FROM tags ")
    category_names = cur.fetchall()
    # creates a form object of the category select form
    category_select_form = CategorySelect(taglist= category_names)
    # SQL query to fetch the title, author and image url of every book in the books table
    selectall = "SELECT authors, title, image_url FROM books LIMIT 10"
    allbooks = text(selectall)
    fetchdata = db.engine.execute(allbooks).fetchall()

    # if statement to make sure the data is entered and validated
    if request.method == 'POST':
      # pulls the information submitted from the form into a dictionary
      data = request.form
      # gets the category from the dictionary data
      category = data['category']
      r = 'sort_by_rating'
      # executes an SQL statement to select book details based on category
      result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ")
      if r in data:
        print(r,'is in dictionary')
        result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ORDER BY average_rating DESC")
      else:
        print(r,'is not in dictionary')
      fetchdata = db.engine.execute(result, category=category)
    
    
    stufftobefiltered = request.args.get('jsdata')
    if stufftobefiltered:
      print(stufftobefiltered)
      filtered_fetchdata = list(filter(lambda x: stufftobefiltered in x[1], fetchdata))
      print(filtered_fetchdata)
      fetchdata = filtered_fetchdata
      return render_template('browse.html',data = fetchdata, form = category_select_form)

    # closes connection object
    cur.close()
    

    # passes fetchdata to the html page so the data can be outputed on the website
    return render_template('browse.html', data = fetchdata, form=category_select_form)





if __name__ == "__main__":  
  app.config['SECRET_KEY'] = '12111111'
  app.run(debug=True)