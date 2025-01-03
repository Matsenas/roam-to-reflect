import os
import requests # type: ignore
import boto3 # type: ignore
import pandas as pd # type: ignore
import time
from pathlib import Path
from dotenv import load_dotenv # type: ignore
from requests.adapters import HTTPAdapter # type: ignore
from urllib3.util.retry import Retry # type: ignore

# Load environment variables from the .env file
load_dotenv()

# Cloudflare R2 S3 configuration
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# Directory configurations
OUTPUT_DIR = Path("output")
LOCAL_DOWNLOAD_FOLDER = Path("downloads")

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Input and output CSV files
file_name = os.getenv("INPUT_FILE")
if not file_name:
    raise ValueError("The 'INPUT_FILE' variable is not set in the .env file.")

INPUT_CSV = OUTPUT_DIR / f"{Path(file_name).stem}.csv"  # Input CSV in the output folder
OUTPUT_CSV = OUTPUT_DIR / "urls-map.csv"                # Output file saved in the output folder

# Initialize the S3 client for R2
s3_client = boto3.client(
    "s3",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    endpoint_url=R2_ENDPOINT_URL,
    region_name="auto",
)

# Create a session with retry logic
def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,  # Retry up to 5 times
        backoff_factor=1,  # Wait: 1s, 2s, 4s, etc.
        status_forcelist=[500, 502, 503, 504],  # Retry for server errors
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session()

def sanitize_file_name(file_name):
    # Replace '%2F' with '/' to retain folder structure.
    return file_name.replace("%2F", "/")

def download_file(firebase_url, local_path):
    # Download a file from Firebase to a local path.
    print(f"Downloading from Firebase")
    try:
        response = session.get(firebase_url, stream=True, timeout=30)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded to: {local_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {firebase_url}: {e}")
        return False

def upload_to_r2(local_path, r2_key):
    # Upload a file to Cloudflare R2 using the S3 API.
    r2_key = str(r2_key)  # Ensure r2_key is a string
    print(f"Uploading to Cloudflare R2: {R2_PUBLIC_URL}/{r2_key}")
    try:
        s3_client.upload_file(str(local_path), R2_BUCKET_NAME, r2_key)
        print(f"Uploaded to R2")
        return True
    except Exception as e:
        print(f"Failed to upload to R2: {e}")
        return False

def process_csv(input_csv, output_csv):
    """Process a CSV file to download from Firebase, upload to R2, and record URLs."""
    # Load the input CSV
    df = pd.read_csv(input_csv)

    # Recover progress if the output file already exists
    if output_csv.exists():
        completed_df = pd.read_csv(output_csv)
        completed_urls = set(completed_df["Firebase URL"])
        print(f"Recovered {len(completed_urls)} completed URLs.")
    else:
        completed_urls = set()

    # Prepare output DataFrame
    if output_csv.exists():
        output_df = pd.read_csv(output_csv)
    else:
        output_df = pd.DataFrame(columns=["Firebase URL", "R2 URL"])

    for index, row in df.iterrows():
        firebase_url = row[0]

        # Skip already processed URLs
        if firebase_url in completed_urls:
            continue

        print(f"Processing URL at index {index}: {firebase_url}")
        original_file_name = firebase_url.split("/")[-1].split("?")[0]
        sanitized_file_name = sanitize_file_name(original_file_name)
        local_path = LOCAL_DOWNLOAD_FOLDER / sanitized_file_name.replace("/", "_")

        # Download from Firebase
        if download_file(firebase_url, local_path):
            # Upload to R2
            r2_key = sanitized_file_name  # Use sanitized name with '/' for logical structure
            if upload_to_r2(local_path, r2_key):
                # R2 encodes '/' back to '%2F', so generate the public URL accordingly
                r2_public_url = f"{R2_PUBLIC_URL}/{r2_key.replace('/', '%2F')}"
                new_row = pd.DataFrame(
                    [{"Firebase URL": firebase_url, "R2 URL": r2_public_url}]
                )
            else:
                new_row = pd.DataFrame(
                    [{"Firebase URL": firebase_url, "R2 URL": "Failed to upload"}]
                )

            # Delete the local file
            try:
                os.remove(local_path)
                print(f"Deleted local file: {local_path}")
            except Exception as e:
                print(f"Failed to delete local file: {e}")
        else:
            new_row = pd.DataFrame(
                [{"Firebase URL": firebase_url, "R2 URL": "Failed to download"}]
            )

        # Use pd.concat instead of append
        output_df = pd.concat([output_df, new_row], ignore_index=True)

        # Save progress after each row
        output_df.to_csv(output_csv, index=False)
        print(f"Progress saved to {output_csv}")

        # Add a small delay to avoid server throttling
        time.sleep(1)

    print(f"Processing completed. Final file saved to {output_csv}")

def main():
    process_csv(INPUT_CSV, OUTPUT_CSV)

if __name__ == "__main__":
    main()