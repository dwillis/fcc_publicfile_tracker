import csv
import requests

# CSV file containing the stations' information
input_csv_file = 'urban_radio_stations.csv'
output_csv_file = 'urban_radio_stations_checked.csv'

# FCC API endpoint
api_url = "https://publicfiles.fcc.gov/api/service/facility/search/"

# Dictionary to map full state names to their two-letter abbreviations
states_to_abbreviations = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

def search_station_on_fcc(station_name):
    """Search the FCC API for a given station name and return the response."""
    if "/" in station_name:
        station_name = station_name.split('/')[0]
    elif "-" in station_name:
        station_name = station_name.split('-')[0]
    response = requests.get(api_url + station_name)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code} for station {station_name}")
        return None

def get_service_profile_url(service_code, call_sign):
    """Generate the FCC URL for the station's profile page, with a maximum 7-character call sign."""
    service_code_map = {
        'AM': 'am-profile',
        'FM': 'fm-profile',
        # Add additional mappings if needed
    }
    profile_type = service_code_map.get(service_code, '').lower()

    # Ensure the call sign is in lowercase and limited to 7 characters
    truncated_call_sign = call_sign.upper()[:7]

    if profile_type:
        return f"https://publicfiles.fcc.gov/{profile_type}/{truncated_call_sign}/rss"
    return ""


def process_csv_and_generate_output(input_csv_file, output_csv_file):
    """Read the input CSV, query FCC API, and write results with matching info to output CSV."""
    with open(input_csv_file, newline='', encoding='utf-8') as input_file, open(output_csv_file, mode='w', newline='', encoding='utf-8') as output_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames + ['City Match', 'State Match', 'FCC URL']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        # Write the header for the new CSV
        writer.writeheader()

        for row in reader:
            station_name = row['Station'].strip()
            expected_city = row['City'].strip().upper()
            expected_state = row['State'].strip()
            expected_state_abbr = states_to_abbreviations.get(expected_state, '')

            fcc_data = search_station_on_fcc(station_name)

            city_match = 'No'
            state_match = 'No'
            fcc_url = ""

            if fcc_data:
                am_facilities = fcc_data['results']['globalSearchResults']['amFacilityList'] or []
                fm_facilities = fcc_data['results']['globalSearchResults']['fmFacilityList'] or []
                tv_facilities = fcc_data['results']['globalSearchResults']['tvFacilityList'] or []

                # Combine all facility lists
                all_facilities = am_facilities + fm_facilities + tv_facilities

                for facility in all_facilities:
                    facility_city = facility['communityCity'].upper()
                    facility_state_abbr = facility['communityState']
                    city_matches = facility_city == expected_city
                    state_matches = facility_state_abbr == expected_state_abbr

                    if city_matches:
                        city_match = 'Yes'
                    if state_matches:
                        state_match = 'Yes'

                    service_code = facility['serviceCode']
                    call_sign = facility['callSign']
                    fcc_url = get_service_profile_url(service_code, call_sign)

                    # Assume the first facility is the most relevant match
                    break

            # Update the current row with the match information and write it to the output CSV
            row['City Match'] = city_match
            row['State Match'] = state_match
            row['FCC URL'] = fcc_url
            writer.writerow(row)

# Main Execution
if __name__ == "__main__":
    process_csv_and_generate_output(input_csv_file, output_csv_file)
