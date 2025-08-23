import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# Function to set up stealthy Selenium driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )
    return driver

# Function to handle login
def handle_login(driver, wait, email, password):
    try:
        print("Step: Navigating to Copilot homepage")
        driver.get("https://copilot.microsoft.com/")
        time.sleep(7)  # Increased wait for page load
        try:
            print("Step: Checking for chat interface (cib-serp)")
            serp = wait.until(EC.presence_of_element_located((By.TAG_NAME, "cib-serp")))
            print("Already logged in, chat interface found.")
            return True
        except Exception as e:
            print(f"No chat interface found, attempting login: {e}")

        print("Step: Clicking sign-in button")
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":r18:"]')))
        sign_in_button.click()
        time.sleep(3)

        print("Step: Clicking second sign-in button if present")
        try:
            second_sign_in = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":r17:"]/div[1]/button')), 5)
            second_sign_in.click()
            print("Clicked second sign-in button.")
            time.sleep(2)
        except Exception as e:
            print(f"Second sign-in button not found or not clickable: {e}")

        print("Step: Clicking 'Login with Microsoft' button if present")
        try:
            ms_login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/main/div/div[2]/div[1]/div[2]/div/button[1]')), 5)
            ms_login_btn.click()
            print("Clicked 'Login with Microsoft' button.")
            time.sleep(2)
        except Exception as e:
            print(f"'Login with Microsoft' button not found or not clickable: {e}")

        print("Step: Waiting for Microsoft login page (email input)")
        wait.until(EC.presence_of_element_located((By.ID, "i0116")))
        time.sleep(2)

        print("Step: Entering email")
        email_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="i0116"]')))
        email_field.send_keys(email)
        time.sleep(1)
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="idSIButton9"]')))
        next_button.click()
        time.sleep(2)

        print("Step: Entering password")
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordEntry"]')))
        password_field.send_keys(password)
        time.sleep(1)

        print("Step: Clicking next button after password")
        next_btn_after_pwd = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="view"]/div/div[5]/button')))
        next_btn_after_pwd.click()
        time.sleep(2)

        print("Step: Handling 'Stay signed in?' prompt if present")
        try:
            yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="view"]/div/div[5]/button[1]')), 10)
            yes_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"'Stay signed in?' prompt not found or not clickable: {e}")

        print("Step: Waiting for CAPTCHA or manual verification")
        print("Please complete the CAPTCHA or human verification manually if prompted.")
        for _ in range(3):  # Retry loop for CAPTCHA
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "cib-serp")), 30)
                print("Logged in successfully after manual verification.")
                return True
            except Exception as e:
                print(f"CAPTCHA wait failed, retrying: {e}")
                time.sleep(10)
        print("Failed to login after multiple CAPTCHA attempts.")
        return False
    except Exception as e:
        print(f"Login failed: {e}")
        return False

# Function to get shadow element chain for input
def get_input_box(driver, wait):
    try:
        # Fallback to original Shadow DOM approach if XPath fails
        try:
            input_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userInput"]')))
            print("Input box found via XPath.")
            return input_box
        except Exception:
            print("XPath for input box failed, trying Shadow DOM.")
            serp = wait.until(EC.presence_of_element_located((By.TAG_NAME, "cib-serp")))
            shadow1 = serp.shadow_root
            action_bar = shadow1.find_element(By.ID, "cib-action-bar-main")
            shadow2 = action_bar.shadow_root
            text_input = shadow2.find_element(By.TAG_NAME, "cib-text-input")
            shadow3 = text_input.shadow_root
            input_box = shadow3.find_element(By.ID, "searchbox")
            print("Input box found via Shadow DOM.")
            return input_box
    except Exception as e:
        print(f"Error finding input box: {e}")
        return None

# Function to get the latest response text
def get_latest_response(driver, wait):
    try:
        serp = driver.find_element(By.TAG_NAME, "cib-serp")
        conversation = driver.execute_script('return arguments[0].shadowRoot.getElementById("cib-conversation-main")', serp)
        turns = driver.execute_script('return arguments[0].shadowRoot.querySelectorAll("cib-chat-turn")', conversation)
        if not turns:
            print("No chat turns found.")
            return ""
        last_turn = turns[-1]
        message_groups = driver.execute_script('return arguments[0].shadowRoot.querySelectorAll("cib-message-group.response-message-group")', last_turn)
        if not message_groups:
            print("No response message groups found.")
            return ""
        message_group = message_groups[-1]
        messages = driver.execute_script('return arguments[0].shadowRoot.querySelectorAll("cib-message[source=\"bot\"]")', message_group)
        if not messages:
            print("No bot messages found.")
            return ""
        message = messages[-1]
        content_divs = driver.execute_script('return Array.from(arguments[0].shadowRoot.querySelectorAll("cib-shared > div.ac-textBlock, cib-shared > div.ac-container"))', message)
        response_text = ' '.join([div.text for div in content_divs if div.text])
        print("Response extracted successfully.")
        return response_text
    except Exception as e:
        print(f"Error extracting response: {e}")
        return ""