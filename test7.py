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

def add_comments_to_match(team_a_name, team_b_name, match_date, comments):
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

# Example usage
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
    # Skip
   
]

team_a_name = "GRANADA"
team_b_name = "VALENCIA"
match_date = datetime.now().strftime("%Y-%m-%d")

# Call the function to add comments
add_comments_to_match(team_a_name, team_b_name, match_date, comments)
