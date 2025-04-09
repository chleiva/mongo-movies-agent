import os
import json
import boto3
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_mongo_client = None
_collection = None

def get_mongo_collection():
    """
    Returns the MongoDB collection object, using secrets stored in AWS Secrets Manager.
    Caches the MongoClient for reuse across Lambda invocations.
    """
    global _mongo_client, _collection
    if _collection:
        return _collection

    secret_name = os.environ["SECRET_NAME"]
    region_name = os.environ.get("AWS_REGION", "us-west-2")
    db_name = os.environ.get("MONGODB_DB_NAME", "sample_mflix")

    try:
        session = boto3.session.Session()
        secret_client = session.client(service_name="secretsmanager", region_name=region_name)
        get_secret_value_response = secret_client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(get_secret_value_response["SecretString"])
        uri = secrets["MONGODB_URI"]
    except Exception as e:
        logger.error("Failed to retrieve MongoDB credentials", exc_info=True)
        raise RuntimeError(f"Failed to load MongoDB secrets: {e}")

    _mongo_client = MongoClient(uri, server_api=ServerApi('1'))
    _collection = _mongo_client[db_name]['movies']
    logger.info("MongoDB connection established.")
    return _collection
