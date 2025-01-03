import re
import csv
import pandas as pd # type: ignore
import os
from pathlib import Path
from dotenv import load_dotenv # type: ignore

# Load environment variables from the .env file
load_dotenv()

def extract_and_save_urls(input_file, output_csv):
    """
    Extract Firebase URLs from a text/JSON file and save them to a CSV file.

    Args:
        input_file (str): Path to the input text/JSON file.
        output_csv (str): Path to save the extracted URLs.
    """
    # Regex to match Firebase URLs
    firebase_url_pattern = r"https://firebasestorage\.googleapis\.com[^\s\"')]*token=[^\s\"')]*"

    # Read the file as plain text
    with open(input_file, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Extract matches
    raw_matches = re.findall(firebase_url_pattern, file_content)

    # Separate concatenated URLs
    separated_urls = []
    for match in raw_matches:
        # Split possible concatenated URLs based on delimiters (e.g., `)![](`)
        separated_urls.extend(re.split(r'[!()\[\]]+', match))

    # Remove unwanted characters and clean URLs
    def clean_url(url):
        return url.strip().rstrip('}').rstrip('\\').rstrip('}').rstrip('%7D').rstrip('%7D')  # Removes unwanted endings

    clean_urls = [clean_url(url) for url in separated_urls if url.strip()]

    # Save all matches to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Firebase URLs'])  # Write the header
        for url in clean_urls:
            csvwriter.writerow([url])

    # Print the total number of URLs found
    print(f"Total URLs gathered: {len(clean_urls)}")

def deduplicate_csv(csv):
    """
    Deduplicate rows in a CSV file and save the result to a new CSV file.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to save the deduplicated CSV file.
    """
    # Load the CSV into a pandas DataFrame
    df = pd.read_csv(csv)

    # Drop duplicate rows
    deduplicated_df = df.drop_duplicates()

    # Save the deduplicated DataFrame to a new CSV file
    deduplicated_df.to_csv(csv, index=False)

    # Print deduplication stats
    print(f"Deduplicated CSV saved to: {csv}")
    print(f"Original rows: {len(df)}, Unique rows: {len(deduplicated_df)}")

def main():
    # Define directories
    input_dir = Path("input")   # Input directory
    output_dir = Path("output") # Output directory

    # Ensure the directories exist
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get the file name from the .env file
    file_name = os.getenv("INPUT_FILE")
    if not file_name:
        raise ValueError("The 'INPUT_FILE' variable is not set in the .env file.")

    # File paths
    input_file = input_dir / file_name  # Input file from .env
    output_csv = output_dir / f"{Path(file_name).stem}.csv"  # Output file with the same name but CSV extension

    # Step 1: Extract URLs and save to CSV
    extract_and_save_urls(input_file, output_csv)

    # Step 2: Deduplicate the CSV
    deduplicate_csv(output_csv)

if __name__ == "__main__":
    main()