from pymongo import MongoClient
from datetime import datetime
# from utils import *
from constants import *
import hashlib

# Connect to MongoDB
mongodb_client = MongoClient(MONGODB_CON_STR)
db = mongodb_client.celery
collection = db.comments

def generate_match_id(team_a_name, team_b_name, match_date):

    team_a_name = team_a_name.upper()
    team_b_name = team_b_name.upper()

    # Get the first half of each team name
    team_a_half = team_a_name[:len(team_a_name) // 2]
    team_b_half = team_b_name[:len(team_b_name) // 2]

    # Combine the halves with the match date
    id_string = f"{team_a_half}{team_b_half}{match_date}"

    # Generate a consistent hash from the combined string
    match_id = hashlib.md5(id_string.encode()).hexdigest()

    return match_id

match_date = datetime.now().strftime("%Y-%m-%d")

teams = ['villarreal', 'atletico-madrid']

# data = generate_match_id(teams[0], teams[1], match_date)

# print(data)

# 47d17f4d7f6e98014e4de78c31de9bc8

match_id = "30242bf985026810b89f792f7ef87110"

# collection.update_one({"_id": match_id}, {"$setOnInsert": {"_id": match_id, "comments": [],  "tweetable":[], "tweeted":[]}}, upsert=True)


base_url = "https://www.goal.com/en-za/match/celta-vigo-vs-valencia/ULKCGal_IhH82Jr1wu0Rq"
minor_url = "https://africa.espn.com/football/commentary/_/gameId/704673"


# Insert the initial document with an empty comments array
document = {
    "_id": match_id,
    "espn": minor_url,
    "goal": base_url,
    "comments": [],  # Initialize the comments field as an empty array
    "tweetable": [],
    "tweeted": []
}


try:
    result = collection.insert_one(document)
    print(f"Document inserted with ID: {result.inserted_id}")
except Exception as e:
    print(f"Error inserting document: {e}")