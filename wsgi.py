import os
import zipfile
from app import app  # Assuming your Flask app is in app.py and named 'app'

# Unzip static files (if they exist)
zip_file_path = 'Anonymous.zip'  # Adjust if the file name is different

if os.path.exists(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall('./') # Extracts to the current directory
    os.remove(zip_file_path) # remove zip file after extraction to save space

if __name__ == "__main__":
    app.run()
