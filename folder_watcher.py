## This script watches a folder for new files and processes them when they appear.
## The path to the folder to watch is read from the .env file.

import os
from dotenv import load_dotenv
from process_daylio_exports import process_daylio_exports
from transfer import transfer_files

def process_folder(folder_path):
    print(f"Working on {folder_path}")
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    for csv_file in csv_files:
        csv_file_path = os.path.join(folder_path, csv_file)
        if 'processed' not in csv_file_path:  # Skip files in the 'processed' subdirectory
            print(f"Processing file: {csv_file_path}")
            process_daylio_exports(csv_file_path)
        else:
            print(f"Skipping file in 'processed' subdirectory: {csv_file_path}")

# Load the configuration from the .env file
load_dotenv()
folder_to_process = os.getenv('WATCH_FOLDER')
export_folder = os.getenv('EXPORT_FOLDER')
remote_host = os.getenv('REMOTE_HOST')
remote_username = os.getenv('REMOTE_USERNAME')
remote_password = os.getenv('REMOTE_PASSWORD')
remote_path = os.getenv('REMOTE_PATH')
transfer_enabled = os.getenv('TRANSFER_ENABLED', 'false').lower() == 'true'

# Process the folder
print(f"Watch folder set in .env: {folder_to_process}")
process_folder(folder_to_process)
print("Processing completed.")

if transfer_enabled:
    print("Transferring files...")
    transfer_files(export_folder, remote_host, remote_username, remote_password, remote_path)
else:
    print("File transfer is disabled.")
