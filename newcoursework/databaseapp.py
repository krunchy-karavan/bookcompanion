from flask import Flask, render_template
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

@app.route('/')
def browse():
    # creates the connection object, which allows us to write SQL queries in the code
    book_tags_df = pd.read_csv('book_tags.csv')
    cur = mysql.connection.cursor()
    cur.execute("SELECT tag_name FROM tags")
    category_names = cur.fetchall()
    exampletags = []
    for i in range(0,10):
      random_category = category_names[random.randint(0,len(category_names))]
      exampletags.append(random_category)
    dropdown = CategorySelect(taglist= category_names)
    print(dir(dropdown))
    

     # SQL query to fetch the title, author and image url of every book in the books table
    category = 'horror'
    result = text("SELECT books.authors, books.title, books.image_url, tags.tag_id FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = :category ")
    fetchdata = db.engine.execute(result, category=category).fetchall()
    #cur.execute("SELECT books.title, books.authors, books.image_url, tags.tag_name FROM ((books INNER JOIN book_tags ON books.goodreads_book_id = book_tags.goodreads_book_id) INNER JOIN tags ON book_tags.tag_id = tags.tag_id) WHERE tags.tag_name = 'horror' " )
    #cur.execute("SELECT title, authors, image_url FROM books")
    # returns all of the data from the SQL query as a list of lists of each book's fetched columns
    #fetchdata = cur.fetchall()
    # closes connection object
    cur.close()
    

    # passes fetchdata to the html page so the data can be outputed on the website
    return render_template('browse.html', data = fetchdata, category_names = exampletags, form=dropdown)





if __name__ == "__main__":  
  app.config['SECRET_KEY'] = '12111111'
  app.run(debug=True)