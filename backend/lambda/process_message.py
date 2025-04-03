import json
import time
import uuid
from common import document_types
from mongodb_tools import insert_update_request
from agent import agent_loop


def search_inflight_request(user_id, request_id):
    # Example simulated response
    return [
        {"message": "Processing your request", "time_stamp": int(time.time())}
    ]

def new_request(user_id, user_request, history):
    # generates new uuid 
    request_id = str(uuid.uuid4())
    response = agent_loop(user_request, history)
    print(f"request:{user_request}\n\nresponse:{response}")
    return request_id, response

def update_inflight_request(user_id, request_id, message):
    insert_update_request(user_id, request_id, message, False)


def handler(event, context):
    method = event.get("httpMethod", "POST")
    headers = {
        "Access-Control-Allow-Origin": event.get('headers', {}).get('origin', '*'),
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "POST,GET,OPTIONS",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            query = event.get("queryStringParameters") or {}
            user_id = query.get("user_id")
            request_id = query.get("request_id")

            if not user_id or not request_id:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "GET request requires both 'user_id' and 'request_id'"})
                }

            messages = search_inflight_request(user_id, request_id)
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "request_id": request_id,
                    "messages": messages
                })
            }

        elif method == "POST":
            body = json.loads(event.get("body", "{}"))
            user_id = body.get("user_id")
            user_request = body.get("request", "").strip()
            history = body.get("history", "")
            print(f"new request: {body}")

            if not user_id:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "Missing 'user_id' in POST request"})
                }

            new_id, response = new_request(user_id, user_request, history)
            if not response or response == "":
                response = "Agent Exception: Apologies, I could not determine the best next action, please try again."
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"request_id": new_id, "response": response})
            }

        elif method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        else:
            return {
                "statusCode": 405,
                "headers": headers,
                "body": json.dumps({"error": f"Method {method} not allowed"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
