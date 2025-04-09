from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import json
import boto3


# Get secret name from environment variable
secret_name = os.environ["SECRET_NAME"]
region_name = os.environ.get("AWS_REGION", "us-west-2")  # fallback default

# Create a Secrets Manager client
session = boto3.session.Session()
secret_client = session.client(service_name="secretsmanager", region_name=region_name)

# Retrieve secret value
get_secret_value_response = secret_client.get_secret_value(SecretId=secret_name)
secrets = json.loads(get_secret_value_response["SecretString"])

uri = secrets["MONGODB_URI"]

# Connect to MongoDB
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
db = mongo_client['sample_mflix']
collection = db['movies']