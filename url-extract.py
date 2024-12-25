import re
import csv

def extract_and_save_urls(input_file, output_csv):
    # Updated regex to match individual Firebase URLs, even when concatenated
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

    # Remove empty strings or invalid entries
    clean_urls = [url.strip() for url in separated_urls if url.strip()]

    # Save all matches to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Firebase URLs'])  # Write the header
        for url in clean_urls:
            csvwriter.writerow([url])

    # Output the total number of URLs found
    print(f"Total URLs gathered: {len(clean_urls)}")

# Replace 'your_file.json' with the path to your JSON file
# Replace 'output_file.csv' with the desired output CSV file name
input_file = 'Roam.json'
output_csv = 'Roam-urls.csv'
extract_and_save_urls(input_file, output_csv)