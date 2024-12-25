import csv

def clean_csv(input_csv, output_csv):
    def clean_url(url):
        # Remove unwanted patterns at the end of the URL
        return url.rstrip('}').rstrip('\\').rstrip('}').rstrip('%7D%7D')

    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        csvreader = csv.reader(infile)
        csvwriter = csv.writer(outfile)

        # Write the header row as is
        header = next(csvreader)
        csvwriter.writerow(header)

        # Process each URL and clean it
        for row in csvreader:
            cleaned_row = [clean_url(row[0])]  # Clean the URL in the first column
            csvwriter.writerow(cleaned_row)

    print(f"Cleaned URLs written to: {output_csv}")

# Replace 'input_file.csv' with the path to your input CSV file
# Replace 'cleaned_file.csv' with the desired output CSV file name
input_csv = 'Reflect-urls.csv'
output_csv = 'clean-Reflect-urls.csv'
clean_csv(input_csv, output_csv)