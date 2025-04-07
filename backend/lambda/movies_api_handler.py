import json
from datetime import datetime
from semantic_search import semantic_search
from resource_movie import create_movie, delete_movie, update_movie, get_movie, list_movies
from mongodb import collection
from bson import ObjectId
from utils import response



def handler(event, context):
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

        elif path == "/movies" and http_method == "GET":
            return list_movies(event)

        elif path == "/movies" and http_method == "POST":
            body = json.loads(event['body'])
            return create_movie(body)

        elif path.startswith("/movies/") and movie_id:
            
            if http_method == "GET":
                return get_movie(movie_id)
            
            elif http_method == "PUT":
                body = json.loads(event['body'])
                return update_movie(movie_id, body)
            
            elif http_method == "DELETE":
                return delete_movie(movie_id)

        return response(400, {'message': 'Invalid request'})
    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        traceback.print_exc()
        return response(500, {'error': 'Unexpected server error', 'details': str(e)})
