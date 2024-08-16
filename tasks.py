import time
# Import the Celery library
from celery import Celery
from constants import *
from pymongo import MongoClient

from flask import jsonify

# Create a Celery instance named 'app'
app = Celery('tasks', backend=MONGODB_CON_STR,
             broker='amqp://guest@localhost//')

# mongodb_client = PyMongo(app, uri=MONGODB_CON_STR)
mongodb_client = MongoClient(MONGODB_CON_STR)
# client = MongoClient("mongodb://localhost:27017/")
db = mongodb_client.celery
# db = client.test_database

# Define a Celery task named 'add'


@app.task()
def add(x, y):
    # Simulate a delay of 25 seconds (for demonstration purposes)
    time.sleep(25)

    # Perform the addition operation
    result = x + y

    # Return the result of the addition
    return result


@app.task()
def add_two():
    db.tasks.insert_one({'title': "THE NOTORIOUS B.I.G.",
                         'body': "NEVER KEEP NO WEIGHT ON YOU"})
    return {"message": "success"}
