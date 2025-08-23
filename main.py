from config import EMAIL, PASSWORD, DUMMY_QUERIES  # Import constants
from utils import setup_driver  # Import driver setup
from etl import etl_pipeline  # Import ETL function

# Run the script
if __name__ == "__main__":
    driver = setup_driver()
    try:
        etl_pipeline(driver, DUMMY_QUERIES, EMAIL, PASSWORD)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()