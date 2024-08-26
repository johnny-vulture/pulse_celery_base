from pymongo import MongoClient
from datetime import datetime
# from utils import *
from constants import *
import hashlib

# Connect to MongoDB
mongodb_client = MongoClient(MONGODB_CON_STR)
db = mongodb_client.celery
collection = db.comments

 # Import ObjectId if using ObjectId for _id

# Assuming match_id is a string representation of the ObjectId
match_id = "47d17f4d7f6e98014e4de78c31de9bc8"

# Use ObjectId if match_id is an ObjectId
match = collection.find_one({"_id": match_id})

# If match_id is a string and not an ObjectId, use it directly
# match = collection.find_one({"_id": match_id})

if match:
    print("Match found ESPN:", match['espn'])
    print("Match found GOAL:", match['goal'])
else:
    print("No match found.")