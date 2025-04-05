#batch process to create vector embeddings for existing  db['movies'] in client['moviesdb']
#the process will get a batch size of 128 chunks/documents that don't have "narrative_embeddings" at a time and will calculate:
#   1) Vector embeddings for Narrative_Embeddings, natural language concatenation of Type + Title + Plot + Full Plot
#   2) Vector embeddings for Contextual_Embeddings, natural language concatenation of genres, cast, languages, year, imdb, tomatoes, type, directors, awards, countries
#   3) [Experimental] Vector embeddings of poster (only if available) with Natural Language.
#once batch embeddings calculated, results will be stored in same collection.

from pymongo import MongoClient
import os
import time
import requests
from openai import OpenAI

# Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BATCH_SIZE = 128


# Connect to MongoDB
print("[Init] Connecting to MongoDB...")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["sample_mflix"]
collection = db["movies"]
print("[Init] Connected to MongoDB.")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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



def embed_texts(texts, embed_type, max_retries=5):
    print(f"[Embed] Requesting OpenAI embeddings for {len(texts)} {embed_type} texts...")
    retries = 0

    while retries < max_retries:
        try:
            response = client.embeddings.create(
                model="text-embedding-3-large",
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            print(f"[Embed] Received {len(embeddings)} embeddings.")
            return embeddings

        except Exception as e:
            print(f"[Embed] Error embedding {embed_type}: {e}")
            retries += 1
            wait_time = 2 ** retries
            print(f"[Embed] Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    print(f"[Embed] Failed to embed {embed_type} after {max_retries} retries.")
    return [None] * len(texts)


total = 0
def process_batch():
    global total
    print(f"[Batch] Fetching up to {BATCH_SIZE} documents without 'narrative_embeddings'...")
    docs = list(collection.find(
        {"narrative_embeddings": {"$exists": False}},
        limit=BATCH_SIZE
    ))

    if not docs:
        print("[Batch] No more documents to process.")
        return False

    print(f"[Batch] Fetched {len(docs)} documents.")

    narrative_texts = [build_narrative_text(doc) for doc in docs]
    contextual_texts = [build_contextual_text(doc) for doc in docs]


    try:
        narrative_embeddings = embed_texts(narrative_texts, "narrative")
        contextual_embeddings = embed_texts(contextual_texts, "contextual")

        print("[Update] Writing embeddings back to MongoDB...")
        for i, doc in enumerate(docs):
            if narrative_embeddings[i] is None or contextual_embeddings[i] is None:
                print(f"[Skip] Skipping document {_id_str(doc)} due to failed embeddings.")
                continue

            update_fields = {
                "narrative_embeddings": narrative_embeddings[i],
                "contextual_embeddings": contextual_embeddings[i],
            }

            result = collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})
            print(f"[Update] Updated document {_id_str(doc)}. Matched: {result.matched_count}, Modified: {result.modified_count}")
            total += 1

            if i % 10 == 0:
                print(f"[Progress] Processed {i+1}/{len(docs)} documents...")

        print(f"[Success] Processed and updated {total} documents.")
        return True

    except Exception as e:
        print(f"[Error] Exception during embedding or update: {e}")
        return False



def _id_str(doc):
    return str(doc.get("_id", "unknown"))

if __name__ == "__main__":
    print("[Start] Beginning batch embedding process...")
    while process_batch():
        print("[Wait] Sleeping before next batch...\n")
        time.sleep(1)  # Sleep to avoid overloading the API
    print("[Done] All documents processed.")
