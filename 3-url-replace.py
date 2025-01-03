import csv
import re
import os
from pathlib import Path

def replace_urls_in_file(input_file, mapping_csv, output_file):
    """
    Replace Firebase URLs in the input file with corresponding matsenas.ee URLs.

    Args:
        input_file (str): Path to the JSON or text file containing Firebase URLs.
        mapping_csv (str): Path to the CSV file with Firebase-to-matsenas URL mapping.
        output_file (str): Path to save the updated file with replaced URLs.
    """
    # Step 1: Load the mapping CSV into a dictionary
    url_mapping = {}
    with open(mapping_csv, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            firebase_url = row['Firebase URLs'].strip()
            matsenas_url = row['R2 URL'].strip()
            url_mapping[firebase_url] = matsenas_url

    # Step 2: Read the input JSON or text file
    with open(input_file, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Step 3: Replace all instances of Firebase URLs with matsenas URLs
    for firebase_url, matsenas_url in url_mapping.items():
        # Use re.escape to ensure special characters in URLs are treated literally
        file_content = re.sub(re.escape(firebase_url), matsenas_url, file_content)

    # Step 4: Save the updated content to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(file_content)

    print(f"Replacements completed. Updated file saved to: {output_file}")

def main():
    # Directories
    input_dir = Path("input")   # Input folder
    output_dir = Path("output") # Output folder

    # Ensure directories exist
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Input and mapping files
    input_file = input_dir / os.getenv("INPUT_FILE")     # Input file
    mapping_csv = output_dir / "urls-map.csv"            # Mapping file in the output folder

    # Dynamically generate the output file name
    output_file = output_dir / (input_file.stem + "-updated" + input_file.suffix)

    # Execute the replacement
    replace_urls_in_file(input_file, mapping_csv, output_file)

if __name__ == "__main__":
    main()