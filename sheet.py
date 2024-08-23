# working
import pandas as pd
import requests
import io
import os
import time
import sys
import spacy
import json
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from spacy.matcher import Matcher
from openai import OpenAI
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image


# Set the Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Specify the path to the ChromeDriver using the Service class
service = Service('C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

api_key = ""
api_secret = ""
bearer_token = r""
access_token = ""
access_token_secret = ""


# Define your Google Sheets constants
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1I7Iom4TOmiLuGcMps7NxI7TB3mAv05bJGs0fw9l1J6U"
SAMPLE_RANGE_NAME = "'Final_fixture'!A2:H10"




client1 = OpenAI(
    # This is the default and can be omitted
    api_key="",
)



# Load the spaCy language model
nlp = spacy.load("en_core_web_md")

# remove team names from comment so prompts are clearer

# turn href into  a mash of team names


def normalize_href(href):
    location = href.split('/')[-1]
    normalized_location = re.sub(r'[^\w\s]', '', location).lower()
    return normalized_location

# turn teams names from google sheet into mash


def concatenate_team_names(team_names):
    concatenated_names = ''.join(team_names)
    normalized_location = re.sub(
        r'[^\w\s]', '', concatenated_names.replace(" ", "")).lower()
    return normalized_location

# get fixture data from goal.coms latest fixture page


def goal_links():

    url = 'https://www.goal.com/en-za/laliga/fixtures-results/34pl8szyvrbwcmfkuocjm3r6t'

    driver.get(url)

    def extract_team_names(url):
        # Extract the part of the URL containing the team names
        match = re.search(r'/match/(.*?)-(.*?)/', url)
        if match:
            # Get the team names from the matched groups
            team1 = match.group(1)
            team2 = match.group(2)

            # Combine the team names into a single string
            team_names = team1 + team2

            # Normalize the team names by removing non-alphanumeric characters and converting to lowercase
            normalized_team_names = re.sub(
                r'[^a-zA-Z0-9]', '', team_names).lower()

            return normalized_team_names
        else:
            # Return None if the URL format doesn't match
            return None

    links = []

    my_elements = driver.find_elements(
        By.CLASS_NAME, 'match_match-wrapper__V5uZZ')

    for i, element in enumerate(my_elements):
        data1 = element.find_element(
            By.CLASS_NAME, 'match_match__rxaZt').get_attribute('href')
        data = extract_team_names(data1)
        data = data.replace("vs", "")
        context = {
            'index': f'{i}',
            'hash': data,
            'url': data1
        }
        links.append(context)

    driver.quit()

    return links

# return the base and minor links for match scraping


def minor():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get("values", [])

        current_date = datetime.now()

        for row in values:
            if len(row) >= 8:  # Check if row has enough elements
                date_time_str = row[4]

                fixture_date = datetime.strptime(
                    date_time_str, "%d.%m. %H:%M").replace(year=current_date.year)
                print("Fixture Date:", fixture_date)

                # Calculate time difference in minutes
                time_diff = (fixture_date - current_date).total_seconds() / 60

                # Compare only the dates (day, month, and year)
                if current_date.date() == fixture_date.date() and 0 < time_diff <= 20:
                    team_names = [row[0], row[1]]
                    normalized_team_names = concatenate_team_names(team_names)
                    normalized_team_names = normalized_team_names.replace(
                        "cf", "")
                    match_links = goal_links()

                    temp = ''

                    for item in match_links:
                        if (item['hash'] == normalized_team_names):
                            temp = item['url']

                    print("Normalized Team Names:", normalized_team_names)

                    link = row[7]  # Assuming column H corresponds to index 7
                    print("Link from column H:", link)

                    context = {
                        'goal': temp,
                        'espn': link
                    }

                    print("Time difference (minutes):", time_diff)
                    return context  # Return the link if condition is met

    except HttpError as err:
        print(err)


href = minor()
if href:
    base_url = href['goal']
    print(base_url)
    minor_url = href['espn']
    print(minor_url)