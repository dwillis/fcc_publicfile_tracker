# FCC Public File Tracker

This repository tracks documents submitted to radio station public files via their RSS feeds.

## Description

The FCC Public File Tracker is a project aimed at tracking the contents of public files at selected radio stations, and in particular urban format stations based on [this Wikipedia page](https://en.wikipedia.org/wiki/List_of_urban-format_radio_stations_in_the_United_States).

## Files

- `fetch_radio_stations.py`: Scrapes the list of stations from Wikipedia, creating a CSV file.
- `get_fcc.py`: Uses that CSV file and the FCC's API to try and match RSS URLs to each station.
- `url_checker.py`: Verifies that each RSS feed url works.
- `rss_parser.py`: Takes a clean CSV file of radio stations, retrieves the RSS feed and parses it into JSON.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/dwillis/fcc_publicfile_tracker.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main script:

    ```bash
    python rss_parser.py
    ```

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions or inquiries, please contact [dwillis@gmail.com](mailto:dwillis@gmail.com).
