import time
import re
import json
from celery import Celery
from constants import *
from pymongo import MongoClient

from flask import jsonify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

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

def transform_sentence(sentence, team_names):
    transformed_sentence = None

    for team_name in team_names:
        pattern = r"\(({})\)".format(re.escape(team_name))
        match = re.search(pattern, sentence)

        if match:
            player_and_event = re.sub(pattern, "", sentence).strip()
            transformed_sentence = f"{team_name}: {player_and_event}"
            break

    if transformed_sentence is None:
        transformed_sentence = sentence  # If no match found, retain original sentence

    return transformed_sentence

def scrape_commentary_with_transform(url, team_names):
    try:
        driver.get(url)
        commentary = []

        wait = WebDriverWait(driver, 20)
        table = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'Table__TBODY')))
        comments = table.find_elements(By.CLASS_NAME, 'Table__TR')

        for comment in comments:
            try:
                game_details = comment.find_element(
                    By.CLASS_NAME, 'MatchCommentary__Comment__GameDetails')
                data = transform_sentence(game_details.text, team_names)
                commentary.append(data)
            except NoSuchElementException:
                print("Game details element not found.")
            except Exception as e:
                print(f"Error processing comment: {e}")

        return commentary

    except TimeoutException:
        print("Timeout while waiting for element.")
    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    finally:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error during driver quit: {e}")



def scrape_events():
    
    url = "https://www.goal.com/en-za/match/granada-vs-valencia/1bdpedpbzvhk5qw1sttvc38k4"

    driver.get(f'{url}#key-events')

    # Wait for the events to load
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'single-event_event__cffsV')))
    except Exception as e:
        print(f"Error waiting for events: {e}")
        return []

    events = driver.find_elements(By.CLASS_NAME, 'single-event_event__cffsV')

    scrape_events = []

    for event in events:
        event_data = event.text.replace('\n', ' ').strip()
        scrape_events.append({"event": [event_data]})

    return scrape_events

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
###########################################################

@app.task()
def scrape_comments_task():
    # Example URL of the webpage containing the commentary
    commentary_url = "https://africa.espn.com/football/commentary/_/gameId/674192"

    # List of team names involved in the match
    team_names = ['Alaves', 'Real Sociedad']
    match_comments = scrape_commentary_with_transform(commentary_url, team_names)
    

    return json.dumps({'comments': match_comments})


@app.task()
def scrape_event_task():
    match_event = scrape_events()
    return {'events': match_event}


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
