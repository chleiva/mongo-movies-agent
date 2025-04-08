from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
import os
import json
import boto3
from openai import OpenAI
import random

# Get secret name from environment variable
secret_name = os.environ["SECRET_NAME"]
region_name = os.environ.get("AWS_REGION", "us-west-2")  # fallback default

# Create a Secrets Manager client
session = boto3.session.Session()
secret_client = session.client(service_name="secretsmanager", region_name=region_name)

# Retrieve secret value
get_secret_value_response = secret_client.get_secret_value(SecretId=secret_name)
secrets = json.loads(get_secret_value_response["SecretString"])

# Use the new OpenAI API key
openai_api_key = secrets["OPENAI_API_KEY"]
uri = secrets["MONGODB_URI"]

# Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# Connect to MongoDB
mongo_client = MongoClient(uri, server_api=ServerApi('1'))


#creates vector embeddings with text-embedding-3-large
def create_embeddings(text):
    print (f"creating embeddings, text: {text}")
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=[text]
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"[Embedding Error] Failed to create embedding: {e}")
        return None


# Function that gets a strig and xml tag idemtifier and returns the text between the tags or empty if the tag is not found, in case of any error, return empty string
def get_tag(text, tag):
    try:
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = text.find(start_tag)
        end = text.find(end_tag)
        if start != -1 and end != -1:
            return text[start + len(start_tag):end]
        else:
            return ""
    except Exception as e:
        return ""



def extract_first_xml_element(input_str):
    """
    Extracts:
    1. Text within the first pair of XML-like tags.
    2. The tag name.
    3. The remaining string after the closing tag.
    
    Args:
        input_str (str): The input string to process.
        
    Returns:
        tuple: (inner_text, tag_name, remaining_text) or (None, None, None) if not found
    """
    # Find the first opening tag
    start_tag_open = input_str.find('<')
    if start_tag_open == -1:
        return None, None, None
    
    start_tag_close = input_str.find('>', start_tag_open)
    if start_tag_close == -1:
        return None, None, None
    
    # Extract potential tag name
    tag_name = input_str[start_tag_open + 1:start_tag_close]
    
    # Validate tag name (must be non-empty and contain only word characters)
    if not tag_name or not all(char.isalnum() or char == '_' for char in tag_name):
        return None, None, None
    
    # Find closing tag
    closing_tag = f"</{tag_name}>"
    end_tag_open = input_str.find(closing_tag, start_tag_close)
    if end_tag_open == -1:
        return None, None, None
    
    # Extract inner text
    inner_text = input_str[start_tag_close + 1:end_tag_open]
    
    # Extract remaining text
    end_tag_close = end_tag_open + len(closing_tag)
    remaining_text = input_str[end_tag_close:]
    
    return inner_text, tag_name, remaining_text





def invoke_claude_sonnet_37(prompt):
    """
    Invokes the Anthropic Claude 3 Sonnet model via AWS Bedrock to generate a response.

    :param prompt: A string representing the user query.
    :return: A string containing the AI-generated response.
    """
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime")

    # Set the model ID for Claude 3 Sonnet.
    model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    
    # Configure reasoning parameters with a 2000 token budget
    reasoning_config = {
        "thinking": {
            "type": "enabled",
            "budget_tokens": 2000
        }
    }

    # Define the request payload in the required format.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())

        # Extract and return the response text.
        return model_response["content"][0]["text"]

    except Exception as e:
        print(f"ERROR: Unable to invoke Claude 3 Sonnet. Reason: {str(e)}")
        return f"ERROR: {str(e)}"




def invoke_claude_x(prompt):
    """
    Invokes one of the Anthropic Claude x models via AWS Bedrock to generate a response.
    It randomly selects a starting model and, in case of a ThrottlingException,
    tries the next model in a round-robin manner.

    :param prompt: A string representing the user query.
    :return: A string containing the AI-generated response or an error message.
    """
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime")

    # List of model IDs.
    model_ids = [
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    ]

    # Define the request payload.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Pick a random starting index.
    start_index = random.randint(0, len(model_ids) - 1)
    attempts = 0

    # Try each model in a round-robin fashion.
    while attempts < len(model_ids):
        current_index = (start_index + attempts) % len(model_ids)
        model_id = model_ids[current_index]
        print(f"using FM: {model_id}")
        try:
            response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
            model_response = json.loads(response["body"].read())
            return model_response["content"][0]["text"]
        except Exception as e:
            # If a ThrottlingException is encountered, try the next model.
            if "ThrottlingException" in str(e):
                print(f"Model {model_id} throttled. Trying next model.")
                attempts += 1
                continue
            else:
                print(f"ERROR: Unable to invoke model {model_id}. Reason: {str(e)}")
                return f"ERROR: {str(e)}"

    return "ERROR: All models throttled or unavailable."






def build_narrative_text(doc):
    parts = []

    movie_type = str(doc.get("type", "")).strip()
    if movie_type:
        parts.append(f"This is a {movie_type.lower()}.")

    title = str(doc.get("title", "")).strip()
    if title:
        parts.append(f"It is titled '{title}'.")

    plot = str(doc.get("plot", "")).strip()
    if plot:
        parts.append(f"The plot is: {plot}")

    full_plot = str(doc.get("full_plot", "")).strip()
    if full_plot and full_plot != plot:
        parts.append(f"In more detail, the full plot is as follows: {full_plot}")

    text = " ".join(parts)
    print(f"[Build] Narrative text: {text[:100]}...")  # Print a preview
    return text




def build_contextual_text(doc):
    parts = []

    # Genres
    genres = doc.get("genres")
    if genres:
        genre_list = ", ".join(genres) if isinstance(genres, list) else str(genres)
        parts.append(f"This movie falls under the genres: {genre_list}.")

    # Cast
    cast = doc.get("cast")
    if cast:
        cast_list = ", ".join(cast) if isinstance(cast, list) else str(cast)
        parts.append(f"The cast includes: {cast_list}.")

    # Languages
    languages = doc.get("languages")
    if languages:
        lang_list = ", ".join(languages) if isinstance(languages, list) else str(languages)
        parts.append(f"The spoken language(s) are: {lang_list}.")

    # Year
    year = doc.get("year")
    if isinstance(year, dict) and "$numberInt" in year:
        parts.append(f"It was released in {year['$numberInt']}.")

    # IMDb ratings
    imdb = doc.get("imdb")
    if isinstance(imdb, dict):
        rating = imdb.get("rating")
        if isinstance(rating, dict) and "$numberDouble" in rating:
            parts.append(f"The IMDb rating is {rating['$numberDouble']}.")
        votes = imdb.get("votes")
        if isinstance(votes, dict) and "$numberInt" in votes:
            parts.append(f"It has received {int(votes['$numberInt']):,} votes on IMDb.")

    # Tomatoes ratings
    # Tomatoes ratings
    tomatoes = doc.get("tomatoes")
    if isinstance(tomatoes, dict):
        critic = tomatoes.get("critic", {})
        viewer = tomatoes.get("viewer", {})

        critic_rating = critic.get("rating")
        if isinstance(critic_rating, dict) and "$numberDouble" in critic_rating:
            parts.append(f"Rotten Tomatoes critic rating is {critic_rating['$numberDouble']}.")
        elif isinstance(critic_rating, (int, float)):
            parts.append(f"Rotten Tomatoes critic rating is {critic_rating}.")

        viewer_rating = viewer.get("rating")
        if isinstance(viewer_rating, dict) and "$numberDouble" in viewer_rating:
            parts.append(f"Audience rating on Rotten Tomatoes is {viewer_rating['$numberDouble']}.")
        elif isinstance(viewer_rating, (int, float)):
            parts.append(f"Audience rating on Rotten Tomatoes is {viewer_rating}.")


    # Awards
    awards = doc.get("awards")
    if isinstance(awards, dict):
        text = awards.get("text")
        if text:
            parts.append(f"It has received the following awards: {text}")

    # Countries
    countries = doc.get("countries")
    if countries:
        country_list = ", ".join(countries) if isinstance(countries, list) else str(countries)
        parts.append(f"Produced in: {country_list}.")

    # Type (e.g., movie)
    movie_type = doc.get("type")
    if movie_type:
        parts.append(f"This is a {movie_type.lower()}.")

    # Final output
    text = " ".join(parts)
    print(f"[Build] Contextual text: {text[:100]}...")
    return text




