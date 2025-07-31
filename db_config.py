from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ajeet'
app.config['MYSQL_DB'] = 'head_count_db'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)
