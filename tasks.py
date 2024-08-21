import time
import datetime
import requests
import asyncio
import io
import os
from PIL import Image
import sys
import spacy
import json
import csv
import re
import uuid
import pandas as pd
from spacy.matcher import Matcher
from openai import OpenAI
import re
import json
from celery import Celery
from constants import *
from utils import *
from scrapers import scrape_scores, scrape_commentary_with_transform
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
def scrape_scores_task(url):
    score = scrape_scores(url)
    return score


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

@app.task()
def scrape_append():
    # declare urls
    base_url = "https://www.goal.com/en-za/match/granada-vs-valencia/1bdpedpbzvhk5qw1sttvc38k4"
    minor_url = "https://africa.espn.com/football/commentary/_/gameId/674265"
    
    # get score
    team_names = []

    data = [
         {
        "timestamp":"-",
        "comment":"Match ends, Real Sociedad 1, Alaves 1."
        },
        {
            "timestamp":"90'+11'",
            "comment":"Real Sociedad: Umar Sadiq  is shown the yellow card."
        },
        {
            "timestamp":"90'+11'",
            "comment":"Second Half ends, Real Sociedad 1, Alaves 1."
        },
        {
            "timestamp":"90'+9'",
            "comment":"Real Sociedad: Attempt missed. Mikel Merino  header from the centre of the box misses to the left. Assisted by Umar Sadiq with a cross."
        },
        {
            "timestamp":"90'+9'",
            "comment":"Alaves: Hand ball by Javi Lpez ."
        },
        {
            "timestamp":"90'+8'",
            "comment":"Corner, Alaves. Conceded by Aihen Muoz."
        },
        {
            "timestamp":"90'+7'",
            "comment":"Real Sociedad: Mikel Oyarzabal  is shown the yellow card."
        },
        {
            "timestamp":"90'+6'",
            "comment":"Real Sociedad: Goal! Real Sociedad 1, Alaves 1. Martn Zubimendi  right footed shot from the centre of the box to the bottom left corner. Assisted by Mikel Merino."
        },
        {
            "timestamp":"90'+6'",
            "comment":"Substitution, Alaves. Xeber Alkain replaces Luis Rioja."
        },
        {
            "timestamp":"90'+4'",
            "comment":"Real Sociedad: Attempt saved. Umar Sadiq  header from the centre of the box is saved in the centre of the goal. Assisted by Arsen Zakharyan with a cross."
        },
        {
            "timestamp":"90'+4'",
            "comment":"Corner, Real Sociedad. Conceded by Antonio Sivera."
        },
        {
            "timestamp":"90'+4'",
            "comment":"Real Sociedad: Attempt saved. Arsen Zakharyan  right footed shot from the right side of the six yard box is saved in the bottom right corner. Assisted by Umar Sadiq."
        },
        {
            "timestamp":"90'+3'",
            "comment":"Alaves: Kike Garca  is shown the yellow card for a bad foul."
        },
        {
            "timestamp":"90'+3'",
            "comment":"Real Sociedad: Mikel Merino  wins a free kick in the defensive half."
        },
        {
            "timestamp":"90'+3'",
            "comment":"Alaves: Foul by Kike Garca ."
        },
        {
            "timestamp":"90'+3'",
            "comment":"Substitution, Real Sociedad. Aihen Muoz replaces Kieran Tierney."
        },
        {
            "timestamp":"90'+3'",
            "comment":"Substitution, Real Sociedad. Arsen Zakharyan replaces Takefusa Kubo."
        },
        {
            "timestamp":"90'+2'",
            "comment":"Real Sociedad: Takefusa Kubo  hits the bar with a left footed shot from outside the box."
        },
        {
            "timestamp":"90'+1'",
            "comment":"Real Sociedad: Umar Sadiq  wins a free kick in the defensive half."
        },
        {
            "timestamp":"90'+1'",
            "comment":"Alaves: Foul by Rafa Marn ."
        },
        {
            "timestamp":"90'+1'",
            "comment":"Alaves: Attempt saved. Kike Garca  left footed shot from the right side of the box is saved in the centre of the goal. Assisted by Luis Rioja."
        }
    ]

    # Scrape and print new scores using the scrape_scores function
    current_score =  scrape_scores(base_url)
    if current_score is not None:
        print(f"New Scores: {current_score}")

    team_names_list = list(current_score.keys())
    team_a_name = team_names_list[0]
    team_b_name = team_names_list[1]
    team_names.append(team_a_name)
    team_names.append(team_b_name)

    # get comments
    match_date = datetime.now().strftime("%Y-%m-%d")
    # Scrape and print new commentary using the fetch_comments function
    # commentary =  scrape_commentary_with_transform(minor_url, team_names)
    commentary = data

    add_comments_to_match(team_a_name, team_b_name, match_date, commentary)

    return {"message": "success full scrape done"}

    # appends


@app.task()
def scrape_main():

    new_commentary = []
    all_commentary = []

    # Create a list to store tweetable comments
    tweetable = []

    # Create a list to store tweeted comments
    tweeted = []

    base_url = "https://www.goal.com/en-za/match/granada-vs-valencia/1bdpedpbzvhk5qw1sttvc38k4"
    minor_url = "https://africa.espn.com/football/commentary/_/gameId/674265"

    # Login to the service with provided user credentials
    """
    await tweet_client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    """

    # Example usage:
    # Example usage with a specified duration
    start_time = time.time()
    duration = 10 * 60  # 180 minutes

    # WHEN THE MATCH STARTS INITIALIZE THE FOLLOWING OBJECTS, SCORE, COMMENT, TWEETABLE, TWEETEED
    # EACH WITH A UNIQUE ID INVOLVING THE MATCH SO IT CAN BE FOUND

    try:
        while time.time() - start_time < duration:
            team_names = []

            # Scrape and print new scores using the scrape_scores function
            current_score =  scrape_scores(base_url)
            if current_score is not None:
                print(f"New Scores: {current_score}")

            team_names_list = list(current_score.keys())
            team_a_name = team_names_list[0]
            team_b_name = team_names_list[1]
            team_names.append(team_a_name)
            team_names.append(team_b_name)

            # Scrape and print new commentary using the fetch_comments function
            commentary =  scrape_commentary_with_transform(minor_url, team_names)


            """
                send to mongo here but check for redudency
                comment storage id can be based on date and teams
                check if comment is present before appending
            """


            if len(commentary) > 0:
                for comment_data in commentary:
                    comment_text = comment_data

                    # MONGO HERE
                    if comment_text not in all_commentary:
                        all_commentary.append(comment_text)
                        print("New Commentary:")
                        print(pd.DataFrame([comment_data]))

                        # Additional check to filter out non-relevant comments
                        if any(keyword in comment_text.lower() for keyword in ["goal", "corner", "foul", "free kick", "substitution", "hand ball", "penalty", "offside", "attempt", "yellow card", "red card"]):
                            matches =  extract_sports_events_info(comment_text)

                            # Print the list of matches with correct ratings without duplicates
                            for match in matches:
                                print('Inside matches')
                                # Check if the rating is equal or above 8 and add to tweetable list
                                if match["rating"] >= 8 and comment_text not in tweetable:
                                    tweetable.append(comment_text)

                                    # Generate soccer comment
                                    tweeter_post =  generate_soccer_comment(
                                        comment_text)
                                    twitter_comment = tweeter_post['Generated Soccer Comment']
                                    print(f'Twitter post: {twitter_comment}')

                                    # Generate prompt for image
                                    generated_prompt =  generate_prompt(
                                        comment_text)
                                    prompt_text = generated_prompt["Generated Soccer Comment"]
                                    print(f'Generated prompt: {prompt_text}')

                                    # Generate image
                                    image_path =  generate_soccer_moment_image(
                                        prompt_text)
                                    print(
                                        f'Generated image path: {image_path}')

                                    tweeted.append(twitter_comment)

                                    """

                                    # Upload media files and obtain media_ids
                                    media_ids = [
                                        await tweet_client.upload_media(image_path)
                                    ]

                                    # Create a tweet with the provided text and attached media
                                    await tweet_client.create_tweet(
                                        text=twitter_comment,
                                        media_ids=media_ids
                                    )
                                    """

                        else:
                            print(
                                "Comment data does not have the expected structure or is not relevant:", comment_data)
            else:
                print("No new commentary found.")

            # Scrape and print new events using the scrape_events function
            

            time.sleep(15)  # Adjust the interval as needed

    except KeyboardInterrupt:
        print("Script interrupted manually.")
    finally:
        # Write tweetable and tweeted data to a CSV file
        combined_data = [{'Tweetable': tweetable_item, 'Tweeted': tweeted_item}
                         for tweetable_item, tweeted_item in zip(tweetable, tweeted)]

        csv_file_path = "tweetable_and_tweeted.csv"

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Tweetable', 'Tweeted']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()

            for combined_item in combined_data:
                writer.writerow(
                    {'Tweetable': combined_item['Tweetable'], 'Tweeted': combined_item['Tweeted']})

        driver.quit()

        print("Script finished.")

        

