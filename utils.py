import re
import requests
import asyncio
import io
import os
from PIL import Image
import time
import sys
import spacy
import json
import csv
import re
import uuid
import pandas as pd
import hashlib
from spacy.matcher import Matcher
from openai import OpenAI
#from twikit import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from scrapers import *
from datetime import datetime
from pymongo import MongoClient
from constants import MONGODB_CON_STR


# Set the Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Create a global WebDriver instance
# Specify the path to the ChromeDriver using the Service class
service = Service('C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

USERNAME = ''
EMAIL = ''
PASSWORD = ''

# Initialize client
#tweet_client = Client('en-US')

# Connect to MongoDB
mongodb_client = MongoClient(MONGODB_CON_STR)
db = mongodb_client.celery
collection = db.comments


# Set the API key
client = OpenAI(
    api_key="sk-proj-X0rMQK1SUWBA1SWmj0wHT3BlbkFJiHbyDcOgle0JouwbBbwD")

# Load the spaCy language model
nlp = spacy.load("en_core_web_md")

# Create lists to store events and commentary
new_events = []
all_events = []

# new_commentary = []
# all_commentary = []

# Create a list to store tweetable comments
# tweetable = []

# Create a list to store tweeted comments
# tweeted = []


def extract_sports_events_info(text):

    # Create a Matcher object to find specific patterns in text
    matcher = Matcher(nlp.vocab)

    # Define patterns and associated ratings for various sports events
    patterns_and_ratings = {
        r'goal': 10,
        r'corner': 7,
        r'foul': 6,
        r'Free kick': 8,
        r'substitution': 5,
        r'hand ball': 8,
        r'penalty': 8,
        r'offside': 7,
        r'attempt': 9,
        r'yellow card': 3,
        r'red card': 9,

    }

    # Create an empty list to store matches
    all_matches = []
    seen_text = set()  # Store seen match text to avoid duplicates

    # Process the input text with spaCy and make it lowercase
    doc = nlp(text.lower())

    # Loop through the patterns and ratings and add them to the Matcher
    for pattern, rating in patterns_and_ratings.items():
        pattern_list = [{"LOWER": token.text.lower()}
                        for token in nlp(pattern)]
        matcher.add(pattern, [pattern_list])

    # Use the Matcher to find matches in the text
    matches = matcher(doc)

    # Loop through the matches and extract match information
    for match_id, start, end in matches:
        span = doc[start:end]  # The matched span
        # Find the sentence that contains the matched span
        sentence = next(sent for sent in doc.sents if span.start >=
                        sent.start and span.end <= sent.end)

        match_text = span.text
        # Check if the match text has already been added to avoid duplicates
        if match_text not in seen_text:
            match_info = {
                "match_id": match_id,
                "text": match_text,
                "sentence": sentence.text,
                "rating": patterns_and_ratings.get(match_text, 0)
            }
            all_matches.append(match_info)
            seen_text.add(match_text)

    return all_matches


def generate_soccer_comment(prompt):
    # Create a conversation with the user's prompt
    conversation = [
        {"role": "user", "content": prompt},
        {"role": "system",
         "content": "You will be provided with scraped soccer commentary, and your task is to make it more lively, also reword them, they will be for Twitter posts, put the team name before the tweet like team name: ..."},
    ]

    # Generate multiple completions based on the conversation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
        temperature=0.8,
        max_tokens=50,
        n=4,  # Set n=4 to get four responses
    )

    # Extract and return the assistant's response
    assistant_response = response.choices[0].message.content

    # Create a dictionary containing the generated comment
    result = {"User Prompt": prompt,
              "Generated Soccer Comment": assistant_response}
    return result


def transform_sentence(sentence, team_names):
    # Initialize transformed_sentence to None
    transformed_sentence = None

    # Iterate over each team name
    for team_name in team_names:
        # Create a regex pattern to find the team name in parentheses
        pattern = r"\(({})\)".format(re.escape(team_name.lower()))
        match = re.search(pattern, sentence)

        if match:
            # Remove the team name and format the remaining text
            player_and_event = re.sub(pattern, "", sentence).strip()
            transformed_sentence = f"{team_name}: {player_and_event}"
            break

    # If no match was found, return the original sentence
    if transformed_sentence is None:
        transformed_sentence = sentence

    return transformed_sentence


def generate_prompt(prompt):
    conversation = [
        {"role": "user", "content": prompt},
        {"role": "system", "content": "you will be given soccer commentary turn it into a prompt i can feed into a stable diffusion model so it can generate an appropriate image from the text, make sure there is accurate limb and face representation"},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
        temperature=0.8,
        max_tokens=50,
    )

    assistant_response = response.choices[0].message.content
    result = {"Generated Soccer Comment": assistant_response}
    return result

# UPDATED
def generate_soccer_moment_image(comment, output_dir=r"C:\Users\User\Desktop\work\pulse_rag_one\test-1\pulse_celery_base\images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    unique_filename = f"{uuid.uuid4()}.jpg"
    output_path = os.path.join(output_dir, unique_filename)

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            print(
                f"Error: API response {response.status_code}, {response.text}")
            return None
        return response.content

    payload = {"inputs": comment}
    image_bytes = query(payload)

    if image_bytes is None:
        print("Error: No image data received")
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(output_path)
        print(f"Image saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_match_id(team_a_name, team_b_name, match_date):
    # Get the first half of each team name
    team_a_half = team_a_name[:len(team_a_name) // 2]
    team_b_half = team_b_name[:len(team_b_name) // 2]

    # Combine the halves with the match date
    id_string = f"{team_a_half}{team_b_half}{match_date}"

    # Generate a consistent hash from the combined string
    match_id = hashlib.md5(id_string.encode()).hexdigest()

    return match_id


def add_comments_to_match(team_a_name, team_b_name, match_date, comments_json):
    match_id = generate_match_id(team_a_name, team_b_name, match_date)

    team_names = [team_a_name, team_b_name]

    scoccer_keywords = ["goal", "corner", "foul", "free kick", "substitution", "hand ball", "penalty", "offside", "attempt", "yellow card", "red card"]
    
    # Convert the JSON string to a list of dictionaries
    comments = json.loads(comments_json)
    
    # Insert the initial document with an empty comments array or update if it exists
    collection.update_one({"_id": match_id}, {"$setOnInsert": {"_id": match_id, "comments": []}}, upsert=True)
    
    # Push each comment into the comments array of the document only if it's not already present
    for comment in comments:
        try:
            # Check if the comment already exists in the document
            existing_comment = collection.find_one({"_id": match_id, "comments": {"$elemMatch": {"comment": comment["comment"]}}})
            existing_tweet = collection.find_one({"_id": match_id, "tweetable": {"$elemMatch": {"text": comment["comment"]}}})

            if not existing_comment:
                # If the comment doesn't exist, push it into the comments array

                comment_text = transform_sentence(comment['comment'],team_names )

                collection.update_one({"_id": match_id}, {"$push": {"comments": comment}})

                # RANK
                if any(keyword in comment_text.lower() for keyword in scoccer_keywords):
                    matches =  extract_sports_events_info(comment_text)
                    # Print the list of matches with correct ratings without duplicates
                    for match in matches:
                        print('Inside matches')
                         # Check if the rating is equal or above 8 and add to tweetable list
                        if match["rating"] >= 8 and not existing_tweet:
                            # tweetable.append(comment_text)
                            collection.update_one({"_id": match_id}, {"$push": {"tweetable": {'timestamp':comment['timestamp'],'text':comment_text}}})

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

                            #tweeted.append(twitter_comment)
                            #add a checker
                            collection.update_one({"_id": match_id}, {"$push": {"tweeted": {'timestamp':comment['timestamp'],'text':twitter_comment}}})
                else:
                    print(
                        "Comment data does not have the expected structure or is not relevant:", comment_text)
                # CHECK
                #print(f"Comment added: {comment['comment']}")
                print(f"Comment added: {comment_text}")
            else:
                print(f"Comment already exists: {comment['comment']}")
        except Exception as e:
            print(f"An error occurred while adding comment: {e}")



#######################################################
"""
def main():
    base_url = "https://www.goal.com/en-za/match/granada-vs-valencia/1bdpedpbzvhk5qw1sttvc38k4"
    minor_url = "https://africa.espn.com/football/commentary/_/gameId/674265"

    # Login to the service with provided user credentials
    
    await tweet_client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    

    # Example usage:
    # Example usage with a specified duration
    start_time = time.time()
    duration = 20 * 60  # 180 minutes

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
            if commentary:
                for comment_data in commentary:
                    comment_text = comment_data

                    # Check if the comment is not already in all_commentary to avoid duplicates
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

                                    

                                    # Upload media files and obtain media_ids
                                    media_ids = [
                                        await tweet_client.upload_media(image_path)
                                    ]

                                    # Create a tweet with the provided text and attached media
                                    await tweet_client.create_tweet(
                                        text=twitter_comment,
                                        media_ids=media_ids
                                    )
                                    

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

        sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
"""