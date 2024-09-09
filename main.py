from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import pyperclip
import os
import pyautogui
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()


# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)


def login_to_twitter(driver, email, username, password):
    driver.get("https://twitter.com/login")
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)

        next_field = WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.NAME, "password")),
                EC.presence_of_element_located((By.NAME, "text"))
            )
        )

        if next_field.get_attribute("name") == "password":
            password_field = next_field
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
        else:
            phone_username_field = next_field
            phone_username_field.send_keys(username)
            phone_username_field.send_keys(Keys.RETURN)
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Home timeline"]'))
        )
        print("Successfully logged in and navigated to the home page.")

        # Schedule tweets based on JSON file
        type_and_schedule_tweets(driver, '/path/to/tweet_contend.json/')

    except TimeoutException:
        print("Timeout while trying to log in")


def type_and_schedule_tweets(driver, json_file):
    successful_tweets = 0
    total_tweets = 0
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if "tweets" in data and data["tweets"]:
            total_tweets = len(data["tweets"])
            for tweet_data in data["tweets"]:
                content = tweet_data.get("content", "")
                schedule = tweet_data.get("schedule", {})
                images = tweet_data.get("images", [])

                if content and schedule:
                    try:
                        # Locate the tweet input element
                        tweet_input = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-testid="tweetTextarea_0"]'))
                        )

                        tweet_input.click()

                        pyperclip.copy(content)
                        tweet_input.send_keys(Keys.CONTROL, 'v')  # Use Keys.COMMAND for Mac

                        print(f"Tweet content '{content}' typed successfully.")

                        # Attach images if any
                        if images:
                            attach_images(driver, images)

                        # Click on the schedule button after typing and attaching images
                        click_schedule_button(driver)

                        # Select the date and time for scheduling
                        select_datetime(driver, **schedule)

                        # Confirm and schedule the tweet
                        click_confirm_button(driver)
                        click_schedule_post_button(driver)

                        print(f"Tweet '{content}' scheduled successfully.")
                        successful_tweets += 1

                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Error scheduling tweet '{content}': {e}")

                    # Refresh the page to avoid stale elements and move to the next tweet
                    time.sleep(10)
                    driver.refresh()

                    # Wait until the home timeline is loaded again
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Home timeline"]'))
                    )
                    print("Page refreshed and ready for the next tweet.")

        # Print the summary at the end
        print(f"\nSummary: {successful_tweets}/{total_tweets} tweets were scheduled successfully.")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error processing tweets: {e}")
    except FileNotFoundError:
        print(f"File {json_file} not found. Please make sure the file exists and the path is correct.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {json_file}. Make sure the JSON is formatted correctly.")

    finally:
        # Ensure that the browser is closed
        time.sleep(30)
        driver.quit()
        print("Browser closed successfully.")


def attach_images(driver, image_paths):
    try:
        for index, image_path in enumerate(image_paths):
            # Adjust the attach button's aria-label depending on the image index
            attach_button_selector = '//button[@aria-label="Add photos or video" and @role="button"]' if index == 0 else '//button[@aria-label="Add media" and @role="button"]'
            
            # Wait until the attach button is clickable and click it
            attach_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, attach_button_selector))
            )
            attach_button.click()
            print(f"Clicked attach button for image {index + 1}.")

            # Short wait for the file dialog to be ready
            time.sleep(1)

            # Ensure the image path is an absolute path
            abs_path = os.path.abspath(image_path)

            # Copy the image path to clipboard
            pyperclip.copy(abs_path)

            # Use pyautogui to paste the path and press Enter
            pyautogui.hotkey('ctrl', 'v')  # On Mac use 'command' instead of 'ctrl'
            pyautogui.press('enter')

            # Wait for the image to upload
            time.sleep(1)

            print(f"Image '{abs_path}' attached successfully ({index + 1}/{len(image_paths)}).")

        print(f"Successfully attached all {len(image_paths)} image(s).")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error attaching images: {e}")


def click_schedule_button(driver):
    try:
        # Wait for the scheduling button to be clickable
        schedule_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Schedule post"][data-testid="scheduleOption"]'))
        )
        schedule_button.click()
        print("Clicked on the scheduling button.")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error locating or clicking on the scheduling button: {e}")


def click_confirm_button(driver):
    try:
        # Wait for the "Confirm" button to be clickable
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="scheduledConfirmationPrimaryAction"]'))
        )
        confirm_button.click()
        print("Clicked on the 'Confirm' button.")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error clicking the 'Confirm' button: {e}")


def click_schedule_post_button(driver):
    try:
        # Wait for the "Schedule" button to be clickable
        schedule_post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="tweetButtonInline"]'))
        )
        schedule_post_button.click()
        print("Clicked on the 'Schedule' button to schedule the tweet.")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error clicking the 'Schedule' button: {e}")

def select_datetime(driver, month, day, year, hour, minute, am_pm):
    try:
        # Select the month
        month_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_1"]'))
        )
        month_dropdown.click()
        month_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_1"]/option[text()="{month}"]')
        month_option.click()
        print(f"Selected month: {month}")

        # Select the day
        day_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_2"]'))
        )
        day_dropdown.click()
        day_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_2"]/option[text()="{day}"]')
        day_option.click()
        print(f"Selected day: {day}")

        # Select the year
        year_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_3"]'))
        )
        year_dropdown.click()
        year_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_3"]/option[text()="{year}"]')
        year_option.click()
        print(f"Selected year: {year}")

        # Select the hour
        hour_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_4"]'))
        )
        hour_dropdown.click()
        hour_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_4"]/option[text()="{hour}"]')
        hour_option.click()
        print(f"Selected hour: {hour}")

        # Select the minute
        minute_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_5"]'))
        )
        minute_dropdown.click()
        minute_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_5"]/option[text()="{minute.zfill(2)}"]')
        minute_option.click()
        print(f"Selected minute: {minute}")

        # Select AM/PM
        am_pm_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'select[id="SELECTOR_6"]'))
        )
        am_pm_dropdown.click()
        am_pm_option = driver.find_element(By.XPATH, f'//select[@id="SELECTOR_6"]/option[text()="{am_pm.upper()}"]')
        am_pm_option.click()
        print(f"Selected AM/PM: {am_pm.upper()}")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error selecting date and time: {e}")


# Log in to Twitter with email, username/phone_number, and password
login_to_twitter(driver, "email", "username/phone_number", "password")