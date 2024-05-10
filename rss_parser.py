import csv
import feedparser
import json

# Input CSV file containing station URLs, states, and cities
csv_file = 'urban_radio_stations_with_status.csv'
# JSON file to save collected data
json_file = 'radio_ads.json'


def parse_feed(station_url, state, city):
    """Parse the RSS feed from the given station URL and include state and city."""
    # Parse the feed using feedparser
    feed = feedparser.parse(station_url)
    
    # List to store extracted entries information
    entries_list = []

    # Iterate over each entry in the RSS feed
    for entry in feed.entries:
        title = entry.title

        # Skip entries where "Issues and Programs Lists" appears in the title
        if "Issues and Programs Lists" in title:
            continue

        link = entry.link
        entry_id = entry.id
        updated = entry.updated

        # Extract the sponsor from the title
        sponsor = title.split('/')[-1]

        # Extract facility ID (uploader) from the title
        try:
            facility_id = int(title.split('Entity ')[1].split(' ')[0])
        except (IndexError, ValueError):
            facility_id = None

        # Extract relevant information from the content
        try:
            file_info = title.split(' in ')[1].split(' on ')
            file_segments = file_info[0].split('/')
            office = file_segments[-2]
        except (IndexError, ValueError):
            office = None

        # Create a dictionary to store the entry information
        entry_dict = {
            "title": title,
            "url": link,
            "id": entry_id,
            "updated": updated,
            "facility_id": facility_id,
            "office": office,
            "sponsor": sponsor,
            "station_url": station_url,
            "state": state,
            "city": city
        }

        # Append the dictionary to the list
        entries_list.append(entry_dict)

    return entries_list


def fetch_rss_entries(csv_file):
    """Fetch RSS entries for each station URL in the provided CSV file."""
    # Load the existing data from radio_ads.json if it exists
    try:
        with open(json_file, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Read the CSV file to get the URLs, state, and city information
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            station_url = row.get('FCC URL')
            state = row.get('State')
            city = row.get('City')
            if station_url:
                # Parse the RSS feed for the current URL, passing state and city
                entries_list = parse_feed(station_url, state, city)
                
                # Add only new entries to the existing data
                for entry in entries_list:
                    entry_id = entry['id']
                    if not any(existing_entry['id'] == entry_id for existing_entry in existing_data):
                        existing_data.append(entry)

    # Write the combined data to radio_ads.json
    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)


# Main execution
if __name__ == "__main__":
    fetch_rss_entries(csv_file)
