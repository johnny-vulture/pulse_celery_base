import time
# Import the Celery library
from celery import Celery
from constants import *
from pymongo import MongoClient

from flask import jsonify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Set the Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Uncomment for headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Specify the path to the ChromeDriver using the Service class
service = Service('C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

# Create a Celery instance named 'app'
app = Celery('tasks', backend=MONGODB_CON_STR,
             broker='amqp://guest@localhost//')

# mongodb_client = PyMongo(app, uri=MONGODB_CON_STR)
mongodb_client = MongoClient(MONGODB_CON_STR)
# client = MongoClient("mongodb://localhost:27017/")
db = mongodb_client.celery
# db = client.test_database

# Define a Celery task named 'add'

def scrape_scores():
    url = "https://www.goal.com/en-za/match/granada-vs-valencia/1bdpedpbzvhk5qw1sttvc38k4"
    driver.get(url)

    try:
        team_A = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'team_team__MFqnv.team_team-a__axhlZ'))
        )

        team_B = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'team_team__MFqnv.team_team-b__kxVXL'))
        )

        score_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'match-data_score__xQ29z'))
        )
    except TimeoutException as e:
        print(f"Error waiting for elements: {e}")
        return None

    team_a_name = team_A.find_element(By.CLASS_NAME, 'team_team-name__0U_gn').text
    team_b_name = team_B.find_element(By.CLASS_NAME, 'team_team-name__0U_gn').text

    team_a_logo = team_A.find_element(By.CLASS_NAME, 'team_team-logo__mQB9a').get_attribute('src')
    team_b_logo = team_B.find_element(By.CLASS_NAME, 'team_team-logo__mQB9a').get_attribute('src')

    scores = score_element.text.split(' - ')

    if len(scores) == 2:
        home_score = scores[0].strip()
        away_score = scores[1].strip()
        score_data = {team_a_name: home_score, team_b_name: away_score}
        return score_data

    return None


@app.task()
def scrape_scores_task():
    score = scrape_scores()
    return {'score': score}


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
