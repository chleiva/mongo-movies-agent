import os
import boto3
import re
import voyageai
from mongodb_tools import insert_document_to_mongo, insert_document_chunk_to_mongo
import random
from common import document_types 
import json


# Get secret name from environment variable
secret_name = os.environ["SECRET_NAME"]
region_name = os.environ.get("AWS_REGION", "us-west-2")  # fallback default

# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(service_name="secretsmanager", region_name=region_name)

# Retrieve secret value
get_secret_value_response = client.get_secret_value(SecretId=secret_name)
secrets = json.loads(get_secret_value_response["SecretString"])

# Now you can access keys inside the secret
voyage_api_key = secrets["VOYAGE_API_KEY"]
mongodb_uri = secrets["MONGODB_URI"]


#----- Helper Functions

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



def create_embeddings(text):
    vo = voyageai.Client(api_key=voyage_api_key)
    result = vo.embed([text], model="voyage-3")
    embedding = result.embeddings[0]
    return embedding

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



def determine_document_metadata(extracted_doc, file_name):
    max_characters = 10000
    document_head = ""
    for i, page_text in enumerate(extracted_doc):
        document_head += page_text
        if len(document_head) > max_characters:
            break
    prompt = f"""
    <DOCUMENT>
    {file_name}
    {document_head}
    </DOCUMENT>

    <TYPES>
    {document_types}
    </TYPES>

    
    TASK
    ----
    You are a document metadata extractor. Your objective is to extract the following metadata from the first pages of the document provided in tags <DOCUMENT></DOCUMENT>:

    - The document name/title
    - The document type (one of the types defined in tags <TYPES>)
    - a description of the document content (answer: What is this document about? and what information does it contain?)
    - manufacturer or brand (only for equipment-specific documents)
    - product model (only for equipment-specific documents), or family product model name/code
    
    RULES
    -----
    - In your output, the only allowed tags you can write are <NAME></NAME>, <TYPE></TYPE>, <DESCRIPTION></DESCRIPTION>, <MANUFACTURER></MANUFACTURER>, <MODEL></MODEL>
    - Ignore any character/text that it is obviously invalid (any OCR extraction inconsistentcy).
    - You should write empty tags when no information is available for a particular attribute, e.g. write <MANUFACTURER></MANUFACTURER> when manufacturer cannot be found in tags <DOCUMENT></DOCUMENT>.
    """
    response = invoke_claude_x(prompt)
    doc_name = get_tag(response, "NAME")
    doc_type = get_tag(response, "TYPE")
    doc_description = get_tag(response, "DESCRIPTION")
    doc_manufacturer = get_tag(response, "MANUFACTURER")
    doc_model = get_tag(response, "MODEL")
    return doc_name, doc_type, doc_description, doc_manufacturer, doc_model


#----- Document Chunking


def chuck_document(extracted_doc, file_name):
    formated_doc = ""
    doc_name, doc_type, doc_description, doc_manufacturer, doc_model = determine_document_metadata(extracted_doc, file_name)
    print(f"Document Name: {doc_name}")
    print(f"Document Type: {doc_type}")
    print(f"Document Description: {doc_description}")
    print(f"Manufacturer: {doc_manufacturer}")
    print(f"Model: {doc_model}")
    insert_document_to_mongo(file_name, doc_name, doc_type, doc_description, doc_manufacturer, doc_model)
    for i, page_text in enumerate(extracted_doc):
        print(f"\n Processing 📄 Page {i + 1} — {len(page_text)} characters")

        prompt = f"""
        <CURRENT_PAGE>
        {page_text}
        </CURRENT_PAGE>


        TASK
        ----
        You are processing a large OCR extracted document, the objective is to organize the document into relevant sections focusing on the current page provided in tags <CURRENT_PAGE>, following these rules:

        RULES
        -----
        - if you identify a Main Heading, write it verbatim in tags <H1></H1>
        - if you identify a Section Heading, write it verbatim in tags <H2></H2>
        - if you identify a Sub-Section Heading, write it verbatim in tags <H3></H3>
        - if you identify any body text or block of text, write it verbatim in tags <BODY></BODY>
        - All the content in tags <CURRENT_PAGE> must be included in your output.
        - In your output, the only allowed tags you can write are <H1></H1>, <H2></H2>, <H3></H3> and <BODY></BODY>.
        - Excludde any character/text that it is obviously invalid (any OCR extraction inconsistentcy).
        """
        response = invoke_claude_x(prompt)
        formated_doc += f"\n<PAGE>{i+1}</PAGE>\n"
        formated_doc += response

    doc = formated_doc
    H1 = ""
    H2 = ""
    H3 = ""
    page = ""

    #print(f"Doc to be processed:\n{doc}")

    structured_document = []

    while (doc):
        text, tag, doc = extract_first_xml_element(doc)

        #print(f"tag = {tag} \n text ={text} ")
         
        if tag == "H1":
            H1 = text
        if tag == "H2":
            H2 = text
        if tag == "H3":
            H3 = text
        if tag == "PAGE":
            page = text
        if tag == "BODY":
            sub_chunk = {
                "H1": H1,
                "H2": H2,
                "H3": H3,
                "page": page,
                "text": text
            }
            structured_document.append(sub_chunk)


    # To group contiguous <BODY> with same H1, H2, H3, and track the initial page
    temp_body = ""
    last_h1, last_h2, last_h3, initial_page = "", "", "", ""

    for sub_chunk in structured_document:
        # Check if we are continuing the same section (same H1, H2, H3)
        if sub_chunk["H1"] == last_h1 and sub_chunk["H2"] == last_h2 and sub_chunk["H3"] == last_h3:
            # If it's the same section, accumulate the body text
            temp_body += "\n" + sub_chunk["text"]
        else:
            # If it's a new section, process the previous accumulated body text as a chunk
            if temp_body:
                process_chunk(file_name, last_h1, last_h2, last_h3, initial_page, temp_body, doc_name, doc_type, doc_description, doc_manufacturer, doc_model)
            # Reset for the new section
            last_h1, last_h2, last_h3, initial_page = sub_chunk["H1"], sub_chunk["H2"], sub_chunk["H3"], sub_chunk["page"]
            temp_body = sub_chunk["text"]  # Start accumulating new body text

    # Process any remaining body content in temp_body after the loop ends
    if temp_body:
        process_chunk(file_name, last_h1, last_h2, last_h3, initial_page, temp_body, doc_name, doc_type, doc_description, doc_manufacturer, doc_model)



def process_chunk(file_name, H1, H2, H3, page, text, doc_name, doc_type, doc_description, doc_manufacturer, doc_model):
    text_to_embed = f"{H1} {H2} {H3} {text}"

    #creates vector embeddings
    embedding = create_embeddings(text_to_embed)

    #now stores the document chunk to MongoDB
    insert_document_chunk_to_mongo(file_name, page, H1, H2, H3, text, embedding, doc_name, doc_type, doc_description, doc_manufacturer, doc_model)