import time
import re
import json
import pandas as pd
from celery import Celery
from constants import *
from pymongo import MongoClient
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

mongodb_client = MongoClient(MONGODB_CON_STR)
db = mongodb_client.celery

def add_two():
    db.tasks.insert_one({'title': "THE NOTORIOUS B.I.G.",
                         'body': "NEVER KEEP NO WEIGHT ON YOU"})
    return {"message": "success"}

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
        transformed_sentence = sentence
    return transformed_sentence

# Instead of trying to decode using 'utf-8', try using 'latin1'
def scrape_commentary_with_transform(url, team_names):
    try:
        driver.get(url)
        commentary = []

        wait = WebDriverWait(driver, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Table__TBODY')))
        comments = table.find_elements(By.CLASS_NAME, 'Table__TR')

        for comment in comments:
            try:
                timestamp = comment.find_element(By.CLASS_NAME, 'MatchCommentary__Comment__Timestamp')
                game_details = comment.find_element(By.CLASS_NAME, 'MatchCommentary__Comment__GameDetails')
                data = transform_sentence(game_details.text, team_names)
                time_stamp = timestamp.text
                commentary.append({"timestamp": time_stamp, "comment": data})
            except NoSuchElementException:
                print("Game details element not found.")
            except Exception as e:
                print(f"Error processing comment: {e}")

        # Convert to DataFrame
        df = pd.DataFrame(commentary)

        # Attempt to decode using 'latin1' if 'utf-8' fails
        df['comment'] = df['comment'].apply(lambda x: x.encode('latin1').decode('utf-8', errors='ignore'))

        return df

    except TimeoutException:
        print("Timeout while waiting for element.")
    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    finally:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error during driver quit: {e}")

commentary_url = "https://africa.espn.com/football/commentary/_/gameId/674192"
team_names = ['Alaves', 'Real Sociedad']

comments_df = scrape_commentary_with_transform(commentary_url, team_names)

# Convert the DataFrame to JSON
comments_json = comments_df.to_json(orient='records', indent=4)

# Print the JSON
print(comments_json)