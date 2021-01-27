from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)
app.static_folder = 'static'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kunsa3002'
app.config['MYSQL_DB'] = 'library'

mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, authors, image_url FROM books LIMIT 10")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template('home.html', data = fetchdata)



if __name__ == "__main__":
    app.run(debug = True)
