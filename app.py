# Import necessary modules from Flask, Celery, and other related modules
from flask import Flask, request, jsonify
from tasks import *
from celery import Celery
from celery.result import AsyncResult
from constants import *
from utils import *
from pymongo import MongoClient
# from flask_pymongo import PyMongo


# Create a Flask app instance
app = Flask(__name__)


# Create a Celery instance named 'celery_app'
celery_app = Celery('tasks', broker='amqp://guest@localhost//')

# mongodb_client = PyMongo(app, uri=MONGODB_CON_STR)
mongodb_client = MongoClient(MONGODB_CON_STR)
# client = MongoClient("mongodb://localhost:27017/")
db = mongodb_client.celery
# db = client.test_database

collection = db.comments

# Configure Celery settings
celery_app.conf.update(
    # Configure the result backend using MySQL

    # 'db+mysql://root:<PASSWORD>@localhost/<DATABASE_NAME>'

    # CELERY_BROKER_URL = "sqlalchemy+mysql://scott:tiger@localhost/foo"
    # backend='db+mysql://username:password@host:port/database'
    # db+mysql://johnny_vulture:dirtyharry_12@localhost/Root80
    # db+mysql://scott:tiger@localhost/foo

    CELERY_RESULT_BACKEND=MONGODB_CON_STR,

    # Set the task serializer to JSON
    CELERY_TASK_SERIALIZER='json',

    # Do not ignore results (set to False)
    CELERY_IGNORE_RESULT=False,

    CELERY_TRACK_STARTED=True,

    CELERY_MONGODB_BACKEND_SETTINGS={
        'database': 'celery',
        'taskmeta_collection': 'tasks',
    },
)

@app.route('/add_match', methods=['POST'])
def run_command(): # nevermind the name its copied code kinda
    goal_url = request.json.get('goal')
    espn_url = request.json.get('espn')
    match_id = request.json.get('match_id')

    # Trigger the Celery task
    task = add_links.apply_async(args=[espn_url, goal_url, match_id])

    # Return the task ID to the client
    return jsonify({'task_id': task.id}), 202

@app.route("/run_match", methods=['POST'])
def run_match_scrape():
    try:
        goal_url = request.json.get('goal')
        espn_url = request.json.get('espn')
        match_id = request.json.get('match_id')
        # result = scrape_append1.delay()  # Ensure you pass the required argument to the task
        # Trigger the Celery task
        result = scrape_match.apply_async(args=[espn_url, goal_url, match_id])
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/full1")
def run_scrape_intervals():
    try:
        # create the match object here
        # Insert the initial document with an empty comments array or update if it exists
        # collection.update_one({"_id": match_id}, {"$setOnInsert": {"_id": match_id, "comments": [],  "tweetable":[], "tweeted":[]}}, upsert=True)
        # post request will create obj based on the data recieved

        # pass the recieved link from the request here  
        result = scrape_append1.delay()  # Ensure you pass the required argument to the task
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500

# Define a route for adding data using a POST request
@app.route("/full")
def run_scrape_full(): #post request
    try:
        # create the match object here
        # Insert the initial document with an empty comments array or update if it exists
        # collection.update_one({"_id": match_id}, {"$setOnInsert": {"_id": match_id, "comments": [],  "tweetable":[], "tweeted":[]}}, upsert=True)
        # post request will create obj based on the data recieved

        # pass the recieved link from the request here  
        result = scrape_append.delay()  # Ensure you pass the required argument to the task
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500



@app.route("/comment")
def run_scrape_comment():
    try:
        result = scrape_comments_task.delay()  # Ensure you pass the required argument to the task
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/score")
def run_scrape():
    try:
        result = scrape_scores_task.delay()  # Ensure you pass the required argument to the task
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500



@app.route("/add_two")
def run_two():
    try:
        add_two.delay()
        return jsonify(message="Task has been submitted successfully"), 202
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/add_one")
def add_one():
    db.tasks.insert_one({'title': "MF DOOM", 'body': "hip hop scifi"})
    return jsonify(message="success")


@app.route('/add', methods=['POST'])
def adddata():
    try:
        # Extract data from JSON request
        data = request.get_json()
        x = data['x']
        y = data['y']

        # Call the 'add' task asynchronously and get the result object
        result = add.delay(x, y)

        # Return the task ID as a JSON response
        return jsonify({'Task ID': result.id, 'Task Status': result.status})
    except Exception as e:
        return jsonify({'error': str(e)})

# Define a route for getting the status of a task


@app.route('/getstatus/<task_id>')
def gettaskstatus(task_id):
    try:
        # Get the status of the task using the task ID
        task_status = celery_app.AsyncResult(task_id).status

        # Return the task status as a JSON response
        return jsonify({'Task Status': task_status})
    except Exception as e:
        return jsonify({'error': str(e)})

# Define a route for getting the result of a completed task


@app.route('/getdone/<task_id>')
def getdone(task_id):
    try:
        # Get the result of the task using the task ID
        task_result = celery_app.AsyncResult(task_id).result

        # Return the task result as a JSON response
        return jsonify({'Task Result': task_result})
    except Exception as e:
        return jsonify({'error': str(e)})

        # mongodb://localhost:27017/


# Run the Flask app in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)
