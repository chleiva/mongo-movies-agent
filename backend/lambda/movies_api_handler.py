"""
Movie API Lambda Handler

Handles CRUD operations and various search strategies (semantic, hybrid, LLM-assisted)
for movie resources via HTTP requests. Designed for deployment as an AWS Lambda
function behind API Gateway.

Routes:
- POST /movies/search
- GET /movies
- POST /movies
- GET /movies/{id}
- PUT /movies/{id}
- DELETE /movies/{id}
"""


import json
from datetime import datetime
from semantic_search import semantic_search
from hybrid_search import hybrid_search
from resource_movie import create_movie, delete_movie, update_movie, get_movie, list_movies
from utils import response
from agent import intelligent_search
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict, context) -> dict:
    """
    AWS Lambda entrypoint for Movie API.

    Routes requests based on the HTTP method and path:
    - /movies/search [POST] — Performs semantic, hybrid, or LLM-assisted search
    - /movies [GET] — Lists all movies
    - /movies [POST] — Creates a new movie
    - /movies/{id} [GET, PUT, DELETE] — Retrieves, updates, or deletes a movie

    Query Parameters:
    - hybrid=true        → enable hybrid search
    - agent=true         → enable LLM-assisted search
    - reranking=true     → enable reranking
    - n={number}         → number of search results

    Parameters:
        event (dict): AWS Lambda event
        context (LambdaContext): AWS Lambda context object

    Returns:
        dict: API Gateway-compatible response object
    """
    http_method = event['httpMethod']
    path = event['path']
    path_params = event.get('pathParameters') or {}
    movie_id = path_params.get('id')
    search_type = ""

    try:
        if path == "/movies/search" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            query = body.get("request", "").strip()

            if not query:
                return response(400, {
                    "error": "Query cannot be empty."
                })
            
            MAX_QUERY_LENGTH = 2048
            if len(query) > MAX_QUERY_LENGTH:
                return response(400, {
                    "error": f"Query too long. Max length is {MAX_QUERY_LENGTH} characters."
                })
            logger.info("Searching movies. Search query: %s", query)

            # Get query parameters
            query_params = event.get("queryStringParameters") or {}
            hybrid = query_params.get("hybrid") == "true"
            agent = query_params.get("agent") == "true"
            reranking = query_params.get("reranking") == "true"
            n = max(1, int(query_params.get("n", 10)))

            # Route to appropriate function
            if agent:
                results = intelligent_search(query)
                search_type = "Hybrid Search (LLM-Assisted). [Note: LLM-assisted search is experimental and may not always yield optimal results.]"
            elif hybrid:
                results = hybrid_search(query, limit=n, reranking=reranking)
                search_type = "Hybrid Search"
            else:
                results = semantic_search(query, limit=n, reranking=reranking)
                search_type = "Semantic Search"

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

        return response(400, {'message': f'Unsupported HTTP method {http_method} for path {path}'})
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        return response(500, {
            'error': 'Unexpected server error',
            'details': str(e)
        })

