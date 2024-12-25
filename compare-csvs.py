import csv
from collections import Counter

def compare_csv_files(file1, file2, output_unmatched_smaller, output_unmatched_bigger):
    # Helper function to load unique URLs from a CSV
    def load_unique_urls(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            csvreader = csv.reader(file)
            next(csvreader)  # Skip the header
            return set(row[0].strip() for row in csvreader)

    # Load unique URLs
    urls_file1 = load_unique_urls(file1)
    urls_file2 = load_unique_urls(file2)

    # Determine smaller and bigger sets
    if len(urls_file1) <= len(urls_file2):
        smaller_csv, bigger_csv = urls_file1, urls_file2
        smaller_name, bigger_name = file1, file2
    else:
        smaller_csv, bigger_csv = urls_file2, urls_file1
        smaller_name, bigger_name = file2, file1

    # Calculate unmatched URLs
    unmatched_in_smaller = smaller_csv - bigger_csv
    unmatched_in_bigger = bigger_csv - smaller_csv

    # Print stats
    print(f"Number of unique URLs in {file1}: {len(urls_file1)}")
    print(f"Number of unique URLs in {file2}: {len(urls_file2)}")
    print(f"Difference in unique URL count: {abs(len(urls_file1) - len(urls_file2))}")
    print(f"Number of unique URLs in smaller CSV ({smaller_name}) that didn't find a match: {len(unmatched_in_smaller)}")
    print(f"Number of unique URLs in bigger CSV ({bigger_name}) that didn't find a match: {len(unmatched_in_bigger)}")

    # Save unmatched URLs to separate files
    with open(output_unmatched_smaller, 'w', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerow(['Unmatched URLs in Smaller CSV'])
        for url in unmatched_in_smaller:
            csvwriter.writerow([url])

    with open(output_unmatched_bigger, 'w', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerow(['Unmatched URLs in Bigger CSV'])
        for url in unmatched_in_bigger:
            csvwriter.writerow([url])

# Replace with the paths to your CSV files and desired output files
file1 = 'clean-Roam-urls.csv'
file2 = 'clean-Reflect-urls.csv'
output_unmatched_smaller = 'unmatched-Reflect.csv'
output_unmatched_bigger = 'unmatched-Roam.csv'

compare_csv_files(file1, file2, output_unmatched_smaller, output_unmatched_bigger)