from pymongo import MongoClient
import os

# Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["sample_mflix"]
collection = db["movies"]

print("[Init] Connected to MongoDB.")

# Define new vector index configurations
index_definitions = [
    {
        "name": "contextual_vector_index",
        "field": "contextual_embeddings",
        "numDimensions": 3072
    },
    {
        "name": "narrative_vector_index",
        "field": "narrative_embeddings",
        "numDimensions": 3072
    }
]

# Drop existing Atlas Search indexes
for idx in index_definitions:
    print(f"🔄 Recreating index: {idx['name']}")
    try:
        db.command({
            "dropSearchIndex": "movies",
            "name": idx["name"]
        })
        print(f"🗑️ Dropped existing index: {idx['name']}")
    except Exception as e:
        print(f"⚠️ Couldn't drop index {idx['name']} (might not exist): {e}")

# Create new Atlas Search indexes
db.command({
    "createSearchIndexes": "movies",
    "indexes": [
        {
            "name": idx["name"],
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        idx["field"]: {
                            "type": "vector",
                            "numDimensions": idx["numDimensions"],
                            "similarity": "cosine"
                        }
                    }
                }
            }
        }
        for idx in index_definitions
    ]
})
print("🎉 All vector indexes updated successfully.")
