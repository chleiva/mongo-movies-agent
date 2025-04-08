from models import create_embeddings, build_contextual_text, build_narrative_text
from mongodb import collection
from bson import ObjectId
from utils import response
from bson import ObjectId
from datetime import datetime


def clean_mongo_document(doc):
    def convert_value(val):
        if isinstance(val, ObjectId):
            return str(val)
        elif isinstance(val, datetime):
            return val.isoformat()
        elif isinstance(val, list):
            return [convert_value(v) for v in val]
        elif isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val

    return {k: convert_value(v) for k, v in doc.items()}


def add_embeddings(data):
    narrative_text = build_narrative_text(data)
    contextual_text = build_contextual_text(data)

    narrative_embeddings = create_embeddings(narrative_text)
    contextual_embeddings = create_embeddings(contextual_text)

    # Add embeddings to data
    data['narrative_embeddings'] = narrative_embeddings
    data['contextual_embeddings'] = contextual_embeddings

    return data




def create_movie(data):
    data = add_embeddings(data)
    result = collection.insert_one(data)
    return response(201, {'_id': str(result.inserted_id)})



def update_movie(movie_id, data):
    data = add_embeddings(data)
    result = collection.update_one({'_id': ObjectId(movie_id)}, {'$set': data})
    if result.matched_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(200, {'message': 'Movie updated'})



def delete_movie(movie_id):
    result = collection.delete_one({'_id': ObjectId(movie_id)})
    if result.deleted_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(204, {'message': 'Movie Deleted.'})



def get_movie(movie_id):
    projection = {
        "contextual_embeddings": 0,
        "narrative_embeddings": 0
    }

    movie = collection.find_one({'_id': ObjectId(movie_id)}, projection)

    if not movie:
        return response(404, {'message': 'Movie not found'})

    movie = clean_mongo_document(movie)
    return response(200, movie)




# Example usage
# GET /movies?page=2&limit=5
def list_movies(event=None):
    # Default pagination values
    default_limit = 10
    default_page = 1

    query_params = event.get("queryStringParameters") or {}
    try:
        page = max(int(query_params.get("page", default_page)), 1)
        limit = min(int(query_params.get("limit", default_limit)), 100)
    except ValueError:
        return response(400, {"message": "Invalid pagination parameters"})

    skip = (page - 1) * limit

    # 👇 Exclude these 3072-dim vectors
    projection = {
        "contextual_embeddings": 0,
        "narrative_embeddings": 0
    }

    total = collection.count_documents({})
    cursor = collection.find({}, projection).skip(skip).limit(limit)
    movies = [clean_mongo_document(doc) for doc in cursor]

    return response(200, {
        "page": page,
        "limit": limit,
        "total": total,
        "movies": movies
    })
