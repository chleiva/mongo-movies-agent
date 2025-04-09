import json
from datetime import datetime
from semantic_search import semantic_search
from hybrid_search import hybrid_search
from resource_movie import create_movie, delete_movie, update_movie, get_movie, list_movies
from utils import response
from agent import intelligent_search


def handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    path_params = event.get('pathParameters') or {}
    movie_id = path_params.get('id')
    search_type = ""

    try:
        if path == "/movies/search" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            query = body.get("request", "")
            print(f"Searching movies. Search query: {query}")

            # Get query parameters
            query_params = event.get("queryStringParameters") or {}
            hybrid = query_params.get("hybrid") == "true"
            agent = query_params.get("agent") == "true"
            reranking = query_params.get("reranking") == "true"
            n = int(query_params.get("n", 10))

            # Route to appropriate function
            if agent:
                results = intelligent_search(query)
                search_type = "Hybrid Search (LLM-Assisted). [Note: LLM-assisted search is experimental and may not always yield optimal results.]"
            elif hybrid:
                results = hybrid_search(query, limit=n, reranking=reranking)
                search_type = " Hybrid Search"
            else:
                results = semantic_search(query, limit=n, reranking=reranking)
                search_type = " Semantic Search"

            return response(200, {
                "message": f"Request completed with {search_type}.",
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
