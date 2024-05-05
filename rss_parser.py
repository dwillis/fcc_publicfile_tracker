import feedparser
import json

def parse_feed(station_name):
    # Determine the URL structure based on the station name
    if station_name.endswith("AM"):
        feed_url = f"https://publicfiles.fcc.gov/am-profile/{station_name.split('-')[0]}/rss"
    else:
        feed_url = f"https://publicfiles.fcc.gov/fm-profile/{station_name.split('-')[0]}/rss"

    # Parse the feed
    feed = feedparser.parse(feed_url)

    # List to store extracted information
    entries_list = []

    # Iterate over entries
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
        facility_id = int(title.split('Entity ')[1].split(' ')[0])

        # Extract relevant information from the content
        file_info = title.split(' in ')[1].split(' on ')
        file_segments = file_info[0].split('/')
        office = file_segments[-2]

        # Create a dictionary to store the entry information
        entry_dict = {
            "title": title,
            "url": link,
            "id": entry_id,
            "updated": updated,
            "facility_id": facility_id,
            "office": office,
            "sponsor": sponsor,
            "station": station_name
        }

        # Append the dictionary to the list
        entries_list.append(entry_dict)

    return entries_list

# List of station names
station_names = [
    "WALR-FM",
    "WAOK-AM",
    "WPZE",
    "WAMJ",
    "WRNB",
    "WGPR",
    # Add more station names here if needed
]

# List to store extracted information from all feeds
all_entries_list = []

# Iterate over station names and parse each feed
for station_name in station_names:
    entries_list = parse_feed(station_name)
    all_entries_list.extend(entries_list)

# Load existing data from radio_ads.json if it exists
try:
    with open('radio_ads.json', 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = []

# Check if each entry's id is already present in the existing data
for entry in all_entries_list:
    entry_id = entry['id']
    # Check if the entry_id already exists in the existing data
    id_exists = any(existing_entry['id'] == entry_id for existing_entry in existing_data)
    # If the entry_id is not present, append the entry to existing data
    if not id_exists:
        existing_data.append(entry)

# Write the combined data to radio_ads.json
with open('radio_ads.json', 'w') as json_file:
    json.dump(existing_data, json_file, indent=4)
