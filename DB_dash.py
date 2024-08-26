import hashlib
from datetime import datetime
from pymongo import MongoClient
from constants import MONGODB_CON_STR
from utils import *

# Connect to MongoDB
mongodb_client = MongoClient(MONGODB_CON_STR)
db = mongodb_client.celery
collection = db.comments

def generate_match_id(team_a_name, team_b_name, match_date):
    # Get the first half of each team name
    team_a_half = team_a_name[:len(team_a_name) // 2]
    team_b_half = team_b_name[:len(team_b_name) // 2]

    # Combine the halves with the match date
    id_string = f"{team_a_half}{team_b_half}{match_date}"

    # Generate a consistent hash from the combined string
    match_id = hashlib.md5(id_string.encode()).hexdigest()

    return match_id

# Example comments to be inserted
comments = [
    {
        "timestamp":"-",
        "comment":"Match ends, Real Sociedad 1, Alaves 1."
    },
    {
        "timestamp":"90'+11'",
        "comment":"Real Sociedad: Umar Sadiq is shown the yellow card."
    },
    {
        "timestamp":"90'+11'",
        "comment":"Second Half ends, Real Sociedad 1, Alaves 1."
    },
    {
        "timestamp":"90'+9'",
        "comment":"Real Sociedad: Attempt missed. Mikel Merino header from the centre of the box misses to the left. Assisted by Umar Sadiq with a cross."
    }
]

# The match ID for the document you want to update
team_a_name = "GRANADA"
team_b_name = "VALENCIA"
match_date = datetime.now().strftime("%Y-%m-%d")
match_id = generate_match_id(team_a_name, team_b_name, match_date)

# Insert the initial document with an empty comments array
document = {
    "_id": match_id,
    "comments": []  # Initialize the comments field as an empty array
}
collection.insert_one(document)

# Push each comment into the comments array of the document
for comment in comments:
    try:
        collection.update_one(
            {"_id": match_id},
            {"$push": {"comments": comment}}
        )
        print(f"Comment added: {comment['comment']}")
    except Exception as e:
        print(f"An error occurred while adding comment: {e}")

def add_match(link1, link2):
    try:
        # Get the base and minor URLs
        base_url = link1
        minor_url = link2

        # Format the date as a string (e.g., '2024-08-25')
        match_date = datetime.now().strftime('%Y-%m-%d')

        # Extract game ID and teams from the minor URL
        game_id, teams = extract_game_id_and_teams(minor_url)

        # Generate match ID
        match_id = generate_match_id1(teams[0], teams[1], match_date)

        # Construct the data dictionary to be inserted
        data = {
            "_id": match_id,
            "goal_link": base_url,
            "espn_link": minor_url,
            "comments": [],
            "tweetable": [],
            "tweeted": []
        }

        # Insert the data into MongoDB (using upsert)
        result = collection.update_one(
            {"_id": match_id},
            {"$setOnInsert": data},
            upsert=True
        )

        # Check if the document was inserted
        if result.upserted_id:
            return {"status": "success", "inserted_id": str(result.upserted_id)}
        else:
            return {"status": "success", "message": "Document already exists"}

    except Exception as e:
        # Log the error and return it
        print(f"Error: {e}")
        return {"error": str(e)}, 500