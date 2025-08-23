import json
import random
import time
import sqlite3
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import handle_login, get_input_box, get_latest_response

# Main ETL pipeline
def etl_pipeline(driver, queries, email, password):
    driver.get("https://copilot.microsoft.com/")
    wait = WebDriverWait(driver, 30)
    
    # Handle login
    if not handle_login(driver, wait, email, password):
        print("ETL aborted due to login failure.")
        return
    
    # Wait for page to fully load
    time.sleep(5)
    
    data = []
    
    for query in queries:
        print(f"Processing query: {query}")
        # Extract: Send query
        input_box = get_input_box(driver, wait)
        if not input_box:
            print(f"Skipping query '{query}' due to input box error.")
            continue
        input_box.clear()  # Clear previous text
        input_box.send_keys(query + Keys.ENTER)
        
        # Wait for response with timeout
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "cib-message-group.response-message-group")))
        except Exception as e:
            print(f"Error waiting for response: {e}")
            continue
        
        # Rate limiting: Random delay 10-30 seconds
        delay = random.uniform(10, 30)
        print(f"Waiting for {delay:.2f} seconds...")
        time.sleep(delay)
        
        # Get response text
        response_text = get_latest_response(driver, wait)
        
        # Transform: Clean the response (strip extra spaces, newlines)
        cleaned_response = ' '.join(response_text.split()).strip()
        
        # Basic analysis: Word count and length
        word_count = len(cleaned_response.split())
        char_length = len(cleaned_response)
        
        # Collect data
        entry = {
            "query": query,
            "response": cleaned_response,
            "word_count": word_count,
            "char_length": char_length
        }
        data.append(entry)
        print(f"Processed query: {query}, Response length: {char_length} chars")
    
    # Load to JSON
    try:
        with open("responses.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Data saved to responses.json")
    except Exception as e:
        print(f"Error saving to JSON: {e}")
    
    # Load to SQLite database
    try:
        conn = sqlite3.connect("copilot_data.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                word_count INTEGER,
                char_length INTEGER
            )
        ''')
        for entry in data:
            cursor.execute('''
                INSERT INTO responses (query, response, word_count, char_length)
                VALUES (?, ?, ?, ?)
            ''', (entry["query"], entry["response"], entry["word_count"], entry["char_length"]))
        conn.commit()
        conn.close()
        print("Data saved to copilot_data.db")
    except Exception as e:
        print(f"Error saving to SQLite: {e}")