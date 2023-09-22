from os import getenv
from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL') #for fly.io add .replace("://", "ql://", 1)
db = SQLAlchemy(app)
