Copilot Scraper Project
This project automates the process of logging into Microsoft Copilot, sending queries, and scraping the responses for further analysis. The responses are saved in both JSON and SQLite formats.

Features
Automated login to Copilot using Selenium with stealth and fake user agent
Sends a list of queries and scrapes the responses
Saves results to responses.json and copilot_data.db
Jupyter notebook for basic data preprocessing and export
Project Structure
main.py — Entry point for running the scraper
etl.py — ETL pipeline for querying and saving responses
utils.py — Helper functions for Selenium automation and scraping
config.py — Configuration for credentials and queries
responses.json — Collected responses in JSON format
copilot_data.db — Collected responses in SQLite format
requirements.txt — Python dependencies
Install dependencies:

pip install -r requirements.txt

Update config.py with your Microsoft account credentials and queries.

Run the scraper:
python main.py

Notes:
Manual intervention may be required for CAPTCHA or verification during login.
The project uses Selenium Stealth and fake-useragent to reduce bot detection.
Data preprocessing includes handling missing values, encoding, and normalization.
