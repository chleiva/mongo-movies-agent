from bson import ObjectId
import json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)



def response(status, body):
    try:
        json_body = json.dumps(body, cls=CustomJSONEncoder, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to serialize body: {e}")
        json_body = json.dumps({"error": "Internal response serialization error"})

    print("Payload preview:", json_body[:500])  # Optional

    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json_body
    }
