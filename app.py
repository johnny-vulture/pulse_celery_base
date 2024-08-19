# Import necessary modules from Flask, Celery, and other related modules
from flask import Flask, request, jsonify
from tasks import add, add_two, scrape_scores_task, scrape_event_task, scrape_comments_task
from celery import Celery
from celery.result import AsyncResult
from constants import *
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


# Define a route for adding data using a POST request

@app.route("/comment")
def run_scrape_comment():
    try:
        result = scrape_comments_task.delay()  # Ensure you pass the required argument to the task
        return jsonify({'Task ID': result.id, 'Task Status': result.status}), 202
    except Exception as e:
        return jsonify(error=str(e)), 500



@app.route("/event")
def run_scrape_event():
    try:
        result = scrape_event_task.delay()  # Ensure you pass the required argument to the task
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
