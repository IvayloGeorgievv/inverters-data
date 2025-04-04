import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_FILE_PREFIX = os.getenv("FILE_PREFIX")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

INVERTERS_NUM = int(os.getenv("INVERTERS_NUM"))
NUM_FILES = int(os.getenv("NUM_FILES"))

#VALID_FILE_PREFIX = os.getenv("VALID_FILE_PREFIX", "valid-data/")
#INVALID_FILE_PREFIX = os.getenv("INVALID_FILE_PREFIX", "invalid-data/")