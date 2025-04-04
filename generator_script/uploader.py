import os
import boto3
from datetime import datetime

from config import AWS_REGION, S3_BUCKET, S3_FILE_PREFIX, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def upload_to_s3(file_name, prefix=""):
    try:
        s3 = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        # Get current date in the desired format
        date_prefix = datetime.now().strftime("%Y-%m-%d/")
        # Combine prefix, date, and file name
        s3_key = f"{S3_FILE_PREFIX}{date_prefix}{os.path.basename(file_name)}"

        s3.upload_file(file_name, S3_BUCKET, s3_key)
        print(f"Uploaded {file_name} to {S3_BUCKET}/{S3_FILE_PREFIX}/{date_prefix}/{prefix}")
        return True
    except Exception as e:
        print(f"Error uploading {file_name}: {e}")
        return False