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



def semantic_search(text, limit=50, filters=None):
    database_name = "sample_mflix"
    document_chunks_collection = "movies"

    db = mongo_client[database_name]
    collection = db[document_chunks_collection]
    print("semantic_search")

    search_embedding = create_embeddings(text)
    if not search_embedding:
        return []

    def build_vector_search_stage(query_vector, embedding_path, index_name, embedding_type_tag):
        print(f"build_vector_search_stage: {embedding_type_tag}")
        stage = {
            "$vectorSearch": {
                "queryVector": query_vector,
                "path": embedding_path,
                "numCandidates": 100,
                "limit": limit,
                "index": index_name
            }
        }

        combined_filter = {}
        if filters:
            combined_filter.update(filters)
        if combined_filter:
            stage["$vectorSearch"]["filter"] = combined_filter

        return [
            stage,
            {
                "$addFields": {
                    "embedding_type": embedding_type_tag,
                    "score": {"$meta": "vectorSearchScore"},
                    "source_embedding": embedding_type_tag
                }
            },
            {
                "$project": {
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
                    "embedding_type": 1,
                    "score": 1,
                    "source_embedding": 1
                }
            }
        ]

    # Pipelines using the same embedding for both paths
    contextual_pipeline = build_vector_search_stage(
        query_vector=search_embedding,
        embedding_path="contextual_embeddings",
        index_name="vector_index",
        embedding_type_tag="contextual"
    )

    narrative_pipeline = build_vector_search_stage(
        query_vector=search_embedding,
        embedding_path="narrative_embeddings",
        index_name="vector_index",
        embedding_type_tag="narrative"
    )

    # Run both searches
    contextual_results = list(collection.aggregate(contextual_pipeline))
    narrative_results = list(collection.aggregate(narrative_pipeline))

    # Deduplicate and keep best scored doc
    merged_results = {}
    for result in contextual_results + narrative_results:
        _id = result["_id"]
        if _id not in merged_results or result["score"] > merged_results[_id]["score"]:
            merged_results[_id] = result

    deduplicated_sorted_results = sorted(merged_results.values(), key=lambda x: x["score"], reverse=True)

    return deduplicated_sorted_results[:limit]
