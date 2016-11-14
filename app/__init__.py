import os

# Import flask and template operators
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
BASE_DIR = os.path.abspath(os.curdir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'db/line-sticker-bot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import models to create tables
import app.models.tweet
import app.models.sequence

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()