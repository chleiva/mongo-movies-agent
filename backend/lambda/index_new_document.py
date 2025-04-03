try:
    import numpy
    print("✅ numpy version:", numpy.__version__)
    print("✅ numpy path:", numpy.__file__)
except Exception as e:
    print("❌ Failed to import numpy:", str(e))



import boto3
import json
import urllib.parse
import os
from embedding import chuck_document

s3_client = boto3.client("s3")
textract_client = boto3.client("textract")



def handler(event, context):
    print("Event received:", json.dumps(event, indent=2))

    # Check if SNS (from Textract async job)
    if "Records" in event and "Sns" in event["Records"][0]:
        sns_message = json.loads(event["Records"][0]["Sns"]["Message"])
        content, doc_name = handle_textract_completion(sns_message)
        chuck_document(content, doc_name)
        return

    # Otherwise, assume it's an S3 event
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        if key.endswith(".txt"):
            content = handle_text_file(bucket, key)
            chuck_document(content, key)
        else:
            start_textract_async(bucket, key)


def handle_text_file(bucket, key, page_char_limit=1800):
    print(f"📄 Reading plain text file: s3://{bucket}/{key}")
    response = s3_client.get_object(Bucket=bucket, Key=key)
    text = response["Body"].read().decode("utf-8").strip()

    ordered_pages = []
    position = 0
    text_len = len(text)

    while position < text_len:
        end = min(position + page_char_limit, text_len)

        # Look backward to the last space to avoid breaking a word
        if end < text_len and text[end].isalnum():
            last_space = text.rfind(" ", position, end)
            if last_space > position:
                end = last_space

        chunk = text[position:end].strip()
        ordered_pages.append(chunk)
        position = end + 1  # move past the space

    return ordered_pages



def start_textract_async(bucket, key):
    print(f"🚀 Starting Textract async job for: s3://{bucket}/{key}")
    response = textract_client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
        NotificationChannel={
            "RoleArn": os.environ["TEXTRACT_ROLE_ARN"],  # Pass via Lambda env vars
            "SNSTopicArn": os.environ["TEXTRACT_SNS_TOPIC_ARN"]
        },
        JobTag=key  # Store the original file name as the JobTag
    )
    print(f"📬 Textract job started with JobId: {response['JobId']}")


def handle_textract_completion(message):
    job_id = message["JobId"]
    status = message["Status"]
    job_tag = message.get("JobTag", "Unknown")  # Retrieve JobTag (which is the original file name)


    if status != "SUCCEEDED":
        print(f"❌ Textract job failed: {status}")
        return

    print(f"✅ Textract job {job_id} completed successfully. Retrieving results...")
    pages = {}
    next_token = None

    while True:
        if next_token:
            response = textract_client.get_document_text_detection(JobId=job_id, NextToken=next_token)
        else:
            response = textract_client.get_document_text_detection(JobId=job_id)

        for block in response.get("Blocks", []):
            if block["BlockType"] == "LINE":
                page = block.get("Page", 1)
                pages.setdefault(page, []).append(block["Text"])

        next_token = response.get("NextToken")
        if not next_token:
            break

    ordered_pages = []
    for page_num in sorted(pages.keys()):
        page_text = "\n".join(pages[page_num])
        ordered_pages.append(page_text)

    return ordered_pages, job_tag
