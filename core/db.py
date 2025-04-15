import pymongo
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

client = pymongo.MongoClient(os.getenv("DB_URI"))
db = client["report_builder"]
collection = db["report_builder"]

def add_query(query: dict, data: list):
    query_id = {
        "_id": query,
        "data": data,
        "created_at": datetime.now()
    }
    collection.insert_one(query_id)
    return query_id


def get_query(query_id: str):
    return collection.find_one({"_id": query_id})


