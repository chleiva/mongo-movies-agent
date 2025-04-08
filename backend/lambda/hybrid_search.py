from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
import os
import json
import boto3
from openai import OpenAI
from models import create_embeddings

# Get secret name from environment variable
secret_name = os.environ["SECRET_NAME"]
region_name = os.environ.get("AWS_REGION", "us-west-2")  # fallback default

# Create a Secrets Manager client
session = boto3.session.Session()
secret_client = session.client(service_name="secretsmanager", region_name=region_name)

# Retrieve secret value
get_secret_value_response = secret_client.get_secret_value(SecretId=secret_name)
secrets = json.loads(get_secret_value_response["SecretString"])

# Use the new OpenAI API key
openai_api_key = secrets["OPENAI_API_KEY"]
uri = secrets["MONGODB_URI"]

# Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# Connect to MongoDB
mongo_client = MongoClient(uri, server_api=ServerApi('1'))



def hybrid_search(text, keyword_search_text = "", keyword_search_categories = [], limit=10, reranking = False):

    if keyword_search_text == "":
        keyword_search_text = text

    if len(keyword_search_categories) == 0:
        keyword_search_categories = ["genres", "cast", "directors", "languages", "year" , "rated", "type"]

    print(f"Running hybrid search for:\nnarrative search: {text}\nkeyword search: {keyword_search_text}\nkeyword search categories: {keyword_search_categories}")
    
    database_name = "sample_mflix"
    collection_name = "movies"
    db = mongo_client[database_name]
    collection = db[collection_name]

    search_embedding = create_embeddings(text)
    if not search_embedding:
        return []

    vector_weight = 0.8
    fulltext_weight = 0.2
    rrf_k = 40  # for Reciprocal Rank Fusion

    if keyword_search_text != text or len(text)<20:
        fulltext_weight = 0.5
        vector_weight = 0.5



    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "narrative_embeddings",
                "queryVector": search_embedding,
                "numCandidates": 100,
                "limit": 20
            }
        },
        {"$group": {"_id": None, "docs": {"$push": "$$ROOT"}}},
        {"$unwind": {"path": "$docs", "includeArrayIndex": "rank"}},
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": [
                        "$docs",
                        {
                            "vs_score": {
                                "$multiply": [
                                    vector_weight,
                                    {"$divide": [1.0, {"$add": ["$rank", rrf_k]}]}
                                ]
                            }
                        }
                    ]
                }
            }
        },
        {
            "$unionWith": {
                "coll": "movies",
                "pipeline": [
                    {
                        "$search": {
                            "index": "movies_text_search_v2",
                            "text": {
                                "query": keyword_search_text,
                                "path": keyword_search_categories
                            }
                        }
                    },
                    {"$limit": 20},
                    {"$group": {"_id": None, "docs": {"$push": "$$ROOT"}}},
                    {"$unwind": {"path": "$docs", "includeArrayIndex": "rank"}},
                    {"$replaceRoot": {
                        "newRoot": {
                            "$mergeObjects": [
                                "$docs",
                                {
                                    "vs_score": 0,  # ensure vs_score is always present
                                    "fts_score": {
                                        "$multiply": [
                                            fulltext_weight,
                                            {"$divide": [1.0, {"$add": ["$rank", rrf_k]}]}
                                        ]
                                    }
                                }
                            ]
                        }
                    }},
                    {"$project": {
                        "_id": 1,
                        "title": 1,
                        "plot": 1,
                        "fullplot": 1,
                        "genres": 1,
                        "runtime": 1,
                        "cast": 1,
                        "poster": 1,
                        "languages": 1,
                        "released": 1,
                        "directors": 1,
                        "rated": 1,
                        "awards": 1,
                        "year": 1,
                        "imdb": 1,
                        "countries": 1,
                        "type": 1,
                        "tomatoes": 1,
                        "num_mflix_comments": 1,
                        "lastupdated": 1,
                        "fts_score": 1,
                        "vs_score": 1
                    }}
                ]
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "doc": { "$first": "$$ROOT" },
                "vs_score": { "$max": "$vs_score" },
                "fts_score": { "$max": "$fts_score" }
            }
        },
        {
            "$replaceRoot": { "newRoot": {
                "$mergeObjects": ["$doc", {
                    "vs_score": { "$ifNull": ["$vs_score", 0] },
                    "fts_score": { "$ifNull": ["$fts_score", 0] }
                }]
            }}
        },
        {"$project": {
            "_id": 1,
            "title": 1,
            "plot": 1,
            "fullplot": 1,
            "genres": 1,
            "runtime": 1,
            "cast": 1,
            "poster": 1,
            "languages": 1,
            "released": 1,
            "directors": 1,
            "rated": 1,
            "awards": 1,
            "year": 1,
            "imdb": 1,
            "countries": 1,
            "type": 1,
            "tomatoes": 1,
            "num_mflix_comments": 1,
            "lastupdated": 1,
            "score": {"$add": ["$vs_score", "$fts_score"]},
            "vs_score": 1,
            "fts_score": 1
        }},
        {"$sort": {"score": -1}},
        {"$limit": limit}
    ]

    results = list(collection.aggregate(pipeline))

    #removes duplicate by _id
    results = list({doc['_id']: doc for doc in results}.values())

    log_output = ["\n--- Final Scores ---"]
    for doc in results:
        title = doc.get('title', 'N/A')
        score = doc.get('score', 0)
        vs_score = doc.get('vs_score', 0)
        fts_score = doc.get('fts_score', 0)

        log_output.append(
            f"Title: {title}\n"
            f"  Combined Score: {score:.8f} "
            f"  Vector Score:   {vs_score:.8f} "
            f"  Fulltext Score: {fts_score:.8f} "
            + "-" * 40
        )

    #print("\n".join(log_output))


    return results
