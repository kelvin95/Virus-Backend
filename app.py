import os
from flask import Flask, request
from flask.ext.restful import Resource, Api, reqparse
from flask.ext.sqlalchemy import SQLAlchemy

from rq import Queue
from worker import conn

q = Queue(connection=conn)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app.config['DEBUG'] = True


api = Api(app)
db = SQLAlchemy(app)

from models import *
from api import *


db.create_all()
'''
virus1 = Virus("Kelvin")
virus2 = Virus("Ulysses")
db.session.add(virus1)
db.session.add(virus2)
db.session.commit()


virus1 = Virus.query.filter_by(name="Kelvin").first()
virus2 = Virus.query.filter_by(name="Ulysses").first()

infection = Infection(virus1, virus2)
db.session.add(infection)
db.session.commit()
'''