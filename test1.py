import time
import re
from celery import Celery
from constants import *
from pymongo import MongoClient

from flask import jsonify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set the Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Uncomment for headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Specify the path to the ChromeDriver using the Service class
service = Service('C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

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


# replace this with bs4 function
def scrape_commentary_with_transform():
    

    url =  "https://africa.espn.com/football/commentary/_/gameId/674192"
    team_names = ['Alaves', 'Real Sociedad']

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
            except Exception as e:
                print(f"Error processing comment: {e}")

        return commentary

    except TimeoutException:
        print("Timeout while waiting for element.")
    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    finally:
        if driver:
            driver.quit()

scrape_commentary_with_transform()