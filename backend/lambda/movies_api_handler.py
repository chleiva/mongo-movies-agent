import json
import os
import boto3
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from semantic_search import semantic_search

# Helper to parse ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# Retrieve MongoDB credentials from AWS Secrets Manager
def get_db_client():
    secret_name = os.environ.get("SECRET_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1")

    client = boto3.client('secretsmanager', region_name=region)
    secret_value = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(secret_value['SecretString'])

    uri = secret['MONGODB_URI']
    return MongoClient(uri)

client = get_db_client()
db = client['sample_mflix']
collection = db['movies']


def get_movie(movie_id):
    movie = collection.find_one({'_id': ObjectId(movie_id)})
    if not movie:
        return response(404, {'message': 'Movie not found'})
    return response(200, movie)


# Helper to parse ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# Retrieve MongoDB credentials from AWS Secrets Manager
def get_db_client():
    secret_name = os.environ.get("SECRET_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1")

    client = boto3.client('secretsmanager', region_name=region)
    secret_value = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(secret_value['SecretString'])

    uri = secret['MONGODB_URI']
    return MongoClient(uri)


def search_movies(query):
    # Perform a text search on the 'title' and 'overview' fields
    # Future: semantic search
    search_query = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"plot": {"$regex": query, "$options": "i"}},
            {"fullplot": {"$regex": query, "$options": "i"}},
        ]
    }
    movies = list(collection.find(search_query).limit(100))
    if not movies:
        return response(200, {'message': 'No movies found'})

    return response(200, {
        'message': 'Displaying list of movies, feel free to ask another question.',
        'movies': movies  # This will be JSON-encoded cleanly via your JSONEncoder
    })


def create_movie(data):
    result = collection.insert_one(data)
    return response(201, {'_id': str(result.inserted_id)})

def update_movie(movie_id, data):
    result = collection.update_one({'_id': ObjectId(movie_id)}, {'$set': data})
    if result.matched_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(200, {'message': 'Movie updated'})

def delete_movie(movie_id):
    result = collection.delete_one({'_id': ObjectId(movie_id)})
    if result.deleted_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(204, None)


def response(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Or restrict to your frontend origin
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps(body, cls=JSONEncoder) if body is not None else ''
    }



def get_movie(movie_id):
    movie = collection.find_one({'_id': ObjectId(movie_id)})
    if not movie:
        return response(404, {'message': 'Movie not found'})
    return response(200, movie)

def list_movies():
    movies = list(collection.find().limit(100))
    return response(200, movies)

def create_movie(data):
    result = collection.insert_one(data)
    return response(201, {'_id': str(result.inserted_id)})

def update_movie(movie_id, data):
    result = collection.update_one({'_id': ObjectId(movie_id)}, {'$set': data})
    if result.matched_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(200, {'message': 'Movie updated'})

def delete_movie(movie_id):
    result = collection.delete_one({'_id': ObjectId(movie_id)})
    if result.deleted_count == 0:
        return response(404, {'message': 'Movie not found'})
    return response(204, None)




def response(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # 👈 Required for CORS
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps(body, cls=JSONEncoder) if body is not None else ''
    }




def handler(event, context):
    #print(f"event:{event}")
    http_method = event['httpMethod']
    path = event['path']
    path_params = event.get('pathParameters') or {}
    movie_id = path_params.get('id')
    try:
        if path == "/movies/search" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            query = body.get("request", "")
            print(f"Searching movies. Search query: {query}")
            results = semantic_search(query)
            return response(200, {
                "message": "Here are your search results.",
                "movies": results
            })
        elif path == "/movies":
            if http_method == 'GET' and movie_id:
                return get_movie(movie_id)
            elif http_method == 'GET':
                return list_movies()
            elif http_method == 'POST':
                body = json.loads(event['body'])
                return create_movie(body)
            elif http_method == 'PUT' and movie_id:
                body = json.loads(event['body'])
                return update_movie(movie_id, body)
            elif http_method == 'DELETE' and movie_id:
                return delete_movie(movie_id)
        return response(400, {'message': 'Invalid request'})
    except Exception as e:
        return response(500, {'error': str(e)})