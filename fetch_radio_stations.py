import csv
import requests
from bs4 import BeautifulSoup

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_urban-format_radio_stations_in_the_United_States"

def fetch_html(url):
    """Fetches the HTML content from the provided URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def parse_stations_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    # Find all sections that potentially contain state information
    # Looking for h2 tags that contain 'mw-headline' to avoid processing irrelevant h2 tags
    state_sections = [h2 for h2 in soup.find_all('h2') if h2.find('span', class_='mw-headline')]

    for state_section in state_sections:
        state_headline = state_section.find('span', class_='mw-headline')
        if not state_headline:
            continue
        state_name = state_headline.get_text()

        # Extract cities and stations under this state
        next_element = state_section.find_next_sibling()
        while next_element and next_element.name != 'h2':
            if next_element.name == 'h3':
                city_headline = next_element.find('span', class_='mw-headline')
                if city_headline:
                    city_name = city_headline.get_text()
                    station_list = next_element.find_next('ul')
                    if station_list:
                        for li in station_list.find_all('li'):
                            parts = li.get_text().split(' – ')
                            station = parts[0]
                            format_description = parts[1] if len(parts) > 1 else "Unknown Format"
                            data.append([state_name, city_name, station, format_description])
            next_element = next_element.find_next_sibling()

    return data

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['State', 'City', 'Station', 'Format'])
        writer.writerows(data)

# Main Execution
if __name__ == "__main__":
    try:
        html_content = fetch_html(url)
        parsed_data = parse_stations_from_html(html_content)
        save_to_csv(parsed_data, 'urban_radio_stations.csv')
        print("Data successfully fetched and saved to 'urban_radio_stations.csv'.")
    except Exception as e:
        raise
        print(f"An error occurred: {e}")
