import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import re

# Cache for pre-signed URLs to avoid generating duplicates
presigned_url_cache = {}

def generate_presigned_s3_url(filename, expiration=3600):
    import os
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError

    bucket_name = os.environ.get("BUCKET_NAME")
    if not bucket_name:
        print("Environment variable BUCKET_NAME is not set.")
        return None

    s3_client = boto3.client('s3')
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=expiration
        )
        return url
    except (NoCredentialsError, ClientError) as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
    

def replace_sources_with_links(text, expiration=3600):
    """
    Replace <SOURCE doc_file_name="..." page="...">...</SOURCE> with markdown links using pre-signed S3 URLs.
    The link text is the original content inside the <SOURCE> tag.
    """
    pattern = r'<SOURCE doc_file_name=[\'"]([^\'"]+)[\'"] page=[\'"]?([^\'"> ]+)[\'"]?>(.*?)</SOURCE>'

    def replacer(match):
        doc = match.group(1)
        page = match.group(2)
        inner_text = match.group(3).strip()

        key = f"{doc}#page={page}"
        if key not in presigned_url_cache:
            base_url = generate_presigned_s3_url(doc, expiration=expiration)
            if base_url:
                presigned_url_cache[key] = f"{base_url}#page={page}"
            else:
                presigned_url_cache[key] = None  # Avoid retrying

        presigned_url = presigned_url_cache.get(key)
        if presigned_url:
            return f'{inner_text} [source 📄]({presigned_url})'
        else:
            return inner_text  # Fallback: plain text

    return re.sub(pattern, replacer, text, flags=re.DOTALL)



