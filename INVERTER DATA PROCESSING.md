
# Introduction

The task was to make a Python script imitating a system sending data to an AWS S3 bucket and process the data inside Snowflake. The script is designed to generate inverter data at regular intervals, validate it and upload it to the S3. The data stored inside the S3 is then automatically loaded into Snowflake using Snowpipe. The whole idea was to gain knowledge on costs for maintaining the S3 bucket and the Snowflake integration. 

# Script Workflow

## 1. Data Generation:

- The script generates inverter data every 20 seconds using the functions `generate_batch_inverter_data` and `generate_inverter_data`.
- Each data records includes metrics such as PAC, energy output, temperature and fault status to follow if there is sensor malfunction.
- The process also includes validation to filter out invalid(incomplete) data. The script is configured to ignore these invalid data records.
## 2. Data Validation:

- Each record is validated by checking each metric against predefined thresholds.
- If any value is outside the acceptable range or is missing the record is marked as invalid.

## 3. Data Upload:

- The script uploads data to the S3 using the function `upload_to_s3`
- Data files are in **JSON** format and are organized in the S3 by date (format: `inverter-data/YYYY-MM-DD/`)

## 4. Threaded Upload:

- Uploading to S3 is performed by a separate thread to avoid blocking the main script and if there is an interruption from user side to don't lose the data from an ongoing upload.

## 5. Error Handling:

- Errors are caught and logged both during data generation and uploading.
- Proper cleanup is performed by deleting local data files after successful upload. That way the script does not try to upload already uploaded files and does not waste local space.

## **Configuration**

For the Python script we need these Environment variables in `.env` file:

``` 
AWS_REGION=us-east-1
S3_BUCKET=my-s3-bucket
S3_FILE_PREFIX=inverter_data/
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
INVERTERS_NUM=60
NUM_FILES=4 
```

**Note:** The `NUM_FILES` is used for speeding up the process inside Snowflake. Instead of consuming 1 big file it is better to separate the records into a few smaller ones. That way we maximize the speed of the process **significantly!**


## **SQL Configuration:**

### 1. Table Structure:

 - Table Name: `INVERTER_DATA_RAW`        
- Fields:
    - `FILE_NAME`: Name of the uploaded file.
    - `JSON_BODY`: The JSON content of the file.
	- `FILE_CONTENT_KEY`: Metadata from the uploaded file.
    - `FILE_LAST_MODIFIED`: Timestamp in UTC when the file was last modified.
    - `START_SCAN_TIME`: Timestamp in UTC when Snowpipe started processing the file.
            
### 2. Snowpipe Configuration:

- Automatically ingests data from the S3 bucket into the `INVERTER_DATA_RAW` table.
- Uses metadata to ensure proper file tracking and timestamp consistency.
## **Running the Script**

1. Install the required packages:
```
pip install -r requirements.txt
```

2. Run the main script:
```
python main.py
```

3. The script will automatically generate, validate, and upload inverter data every 20 seconds.

## **Challenges and Solutions:**

### 1. Directory Structure Issue:

The script initially uploaded files to the root S3 bucket without organizing by date. This was going to make a messy and unorganized structure and was easily fixed by updating the script to create a folder structure based on the current date (YYYY-MM-DD).

### 2. IAM User vs Role Issue:

The script initially worked with a IAM Role that could not assume itself causing permission errors. The fix was to create a new IAM User for the data upload and a separate IAM Role for the Snowflake integration, because Snowflake uses IAM Roles NOT IAM Users.

### 3. Snowpipe Automation issue:

The Snowpipe was not triggered to automatically upload data from the S3. This again was easily fixed by using SQS notification channels by enabling Event Notification for new upload or change of file in the S3.

### 4. Metadata Management Issue:

The Uploaded files metadata had some Timestamps that were not in UTC format. The fix was simply to use **nested SELECT Query** and select the timestamps by converting the timezone with `CONVERT_TIMEZONE('UTC', [field])`.

## **Known Issues and Future Improvements**

- The current implementation only uploads valid data. If needed, the logic for uploading invalid data can be re-enabled by uncommenting the corresponding sections in `generator.py` and `main.py`.
    
- The script could be extended to monitor the upload process and retry in case of failures.
    
- Improve Snowflake integration by adding error monitoring for automatic ingestion.
  
## **Conclusion**

This project demonstrates a robust and modular approach to processing and uploading inverter data while efficiently integrating with Snowflake. It combines data validation, threaded uploads, and automated data ingestion, making it a versatile tool for real-time data processing and storage.