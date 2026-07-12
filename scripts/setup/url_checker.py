import csv
import requests

# Input CSV file
input_csv = 'urban_radio_stations_checked.csv'
# Output CSV file with status code
output_csv = 'urban_radio_stations_with_status.csv'

def check_url_status(url):
    """Check the HTTP status code of a given URL."""
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return None

def add_status_code_to_csv(input_csv, output_csv):
    """Read the input CSV, check URL status codes, and write to the output CSV with the status code."""
    with open(input_csv, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['HTTP Status Code']
        
        with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                url = row.get('FCC URL')
                if url:
                    status_code = check_url_status(url)
                    row['HTTP Status Code'] = status_code
                else:
                    row['HTTP Status Code'] = 'N/A'
                
                writer.writerow(row)

# Main execution
if __name__ == "__main__":
    add_status_code_to_csv(input_csv, output_csv)
