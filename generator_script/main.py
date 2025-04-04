import time
import os
import threading #Threading to finish and active upload process without problem
from datetime import datetime
from generator import generate_batch_inverter_data
from uploader import upload_to_s3
from config import INVERTERS_NUM, NUM_FILES
from utils import delete_files_in_folder


upload_in_progress = threading.Event()
DATA_FOLDER = "data"

def start_uploading():
    try:
        current_date = datetime.now().strftime("%Y-%m-%d") # Get current date for folder insertion in S3
        for file_name in os.listdir(DATA_FOLDER):
            file_path = os.path.join(DATA_FOLDER, file_name)
            if file_name.startswith("inverter-data"):
                upload_to_s3(file_path)
            # Commented out logic for invalid data records insertion because for now we don't need it
            # elif file_name.startswith("invalid_inverter_data"):
            #     upload_to_s3(file_path, INVALID_FILE_PREFIX)
    finally:
        upload_in_progress.clear()

def process_and_upload():
    global upload_in_progress

    print("Generating data...")
    generate_batch_inverter_data(INVERTERS_NUM, NUM_FILES)

    print("Uploading data to S3...")
    upload_in_progress.set()

    upload_thread = threading.Thread(target=start_uploading)
    upload_thread.start()

    #Joining the upload thread ensures that all files are uploaded before the script waits for the next run.
    upload_thread.join()

    delete_files_in_folder(DATA_FOLDER)

    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Process completed at {completion_time}")

if __name__ == "__main__":
    try:
        while True:
            process_and_upload()
            print("Waiting for next run... Press Ctrl+C to exit")
            time.sleep(20)
    except KeyboardInterrupt:
        print("Process interrupted. Cleaning up...")

        if upload_in_progress.is_set():
            print("Upload in progress. Waiting for completion...")

            while upload_in_progress.is_set():
                time.sleep(1)

            print("Upload completed. Exiting...")

        else:
            print("No active upload. Exiting...")

        delete_files_in_folder(DATA_FOLDER)
        print("Process stopped.")