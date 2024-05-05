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

# Write the list of dictionaries to a JSON file
with open('radio_ads.json', 'w') as json_file:
    json.dump(all_entries_list, json_file, indent=4)
