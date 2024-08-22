import hashlib
from datetime import datetime
from pymongo import MongoClient
from constants import MONGODB_CON_STR

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
    },
    {
        "timestamp":"90'+8'",
        "comment":"Corner, Alaves. Conceded by Aihen Muoz."
    },
    #skip
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
]

# The match ID for the document you want to update
team_a_name = "GRANADA"
team_b_name = "VALENCIA"
match_date = datetime.now().strftime("%Y-%m-%d")
match_id = generate_match_id(team_a_name, team_b_name, match_date)

# Insert the initial document with an empty comments array or update if it exists
collection.update_one(
    {"_id": match_id},
    {"$setOnInsert": {"_id": match_id, "comments": []}},
    upsert=True
)

# Push each comment into the comments array of the document only if it's not already present
for comment in comments:
    try:
        # Check if the comment already exists in the document
        existing_comment = collection.find_one(
            {"_id": match_id, "comments.comment": comment["comment"]}
        )
        
        if not existing_comment:
            # If the comment doesn't exist, push it into the comments array
            collection.update_one(
                {"_id": match_id},
                {"$push": {"comments": comment}}
            )
            print(f"Comment added: {comment['comment']}")
        else:
            print(f"Comment already exists: {comment['comment']}")
            
    except Exception as e:
        print(f"An error occurred while adding comment: {e}")



"""
import hashlib
from datetime import datetime
from pymongo import MongoClient
from constants import MONGODB_CON_STR

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
    },
    {
        "timestamp":"90'+8'",
        "comment":"Corner, Alaves. Conceded by Aihen Muoz."
    },
    #skip
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

# Push each comment into the comments array of the document only if it's not already present
for comment in comments:
    try:
        # Check if the comment already exists in the document
        existing_comment = collection.find_one(
            {"_id": match_id, "comments.comment": comment["comment"]}
        )
        
        if not existing_comment:
            # If the comment doesn't exist, push it into the comments array
            collection.update_one(
                {"_id": match_id},
                {"$push": {"comments": comment}}
            )
            print(f"Comment added: {comment['comment']}")
        else:
            print(f"Comment already exists: {comment['comment']}")
            
    except Exception as e:
        print(f"An error occurred while adding comment: {e}")
"""