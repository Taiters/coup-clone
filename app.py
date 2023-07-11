import sqlite3

from flask import Flask
from flask import g

from coup_clone.database import db_session
from coup_clone.database import db_session
from coup_clone.models import User

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def hello_world():
    users = User.query.all()
    user_items = ''.join([f'<li>{u}</li>' for u in users])
    return f'<ul>{user_items}</ul>'

@app.route("/add/<string:name>")
def add_user(name):
    u = User(name)
    db_session.add(u)
    db_session.commit()
    return f'<p>Added {u}</p>'

