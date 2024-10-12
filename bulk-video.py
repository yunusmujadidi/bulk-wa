import openpyxl
import time
import logging
import re
import csv
import os
import pyautogui
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Configure logging
logging.basicConfig(filename='bulk_send_video.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def format_indonesian_number(phone_number):
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    
    # Check if the number starts with '0' or '62'
    if digits.startswith('0'):
        formatted_number = '62' + digits[1:]
    elif digits.startswith('62'):
        formatted_number = digits
    else:
        formatted_number = '62' + digits
    
    # Ensure the number starts with '+62'
    if not formatted_number.startswith('+'):
        formatted_number = '+' + formatted_number
    
    return formatted_number

def load_sent_numbers():
    sent_numbers = set()
    if os.path.exists('sent_numbers_image.csv'):
        with open('sent_numbers_image.csv', 'r') as f:
            reader = csv.reader(f)
            sent_numbers = set(row[0] for row in reader)
    return sent_numbers

def save_sent_number(phone_number):
    with open('sent_numbers_image.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([phone_number])

def load_daily_count():
    if os.path.exists('daily_count_image.csv'):
        with open('daily_count_image.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    last_date, count = row
                    if last_date == str(date.today()):
                        return int(count)
    return 0

def save_daily_count(count):
    with open('daily_count_image.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([str(date.today()), count])

def send_message(driver, phone_number, caption, video_path):
    logging.info(f"Attempting to send message to {phone_number}")
    
    url = f"https://web.whatsapp.com/send?phone={phone_number}"
    driver.get(url)

    try:
        # Wait for the chat to load
        chat_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        
        # Check if the video is already attached
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "media-container")]'))
            )
            logging.info("Video is already attached.")
        except TimeoutException:
            logging.info("Video not attached. Attaching now.")
            # Attach the video
           
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
            )
            file_input.send_keys(video_path)

        # Wait for the caption field to be clickable
        caption_field = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]'))
        )

        # Paste the caption
        caption_field.send_keys(Keys.CONTROL + 'a')  # Select all existing text
        caption_field.send_keys(Keys.DELETE)  # Delete existing text
        caption_field.send_keys(caption)  # Paste new caption

        # Send the message
        caption_field.send_keys(Keys.ENTER)

        # Wait for the upload to complete (adjust the timeout as needed)
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-time"]'))
        )

        logging.info(f"Video sent successfully to {phone_number}")
        return True

    except Exception as e:
        logging.error(f"Failed to send video message to {phone_number}. Error: {str(e)}")
        return False

# Load the XLSX file
workbook = openpyxl.load_workbook('phone_numbers.xlsx')
sheet = workbook.active

# Read phone numbers from the XLSX file and format them
phone_numbers = [format_indonesian_number(cell.value) for cell in sheet['A'] if cell.value]

# Load already sent numbers
sent_numbers = load_sent_numbers()

# Promotional message and video path
message = "Hello! We are excited to share our latest video with you. Check out our amazing products and offers in this short clip.\n\nDon't miss out on our special discounts and promotions. Visit our website to learn more!\n\nyynoes.me"
video_path = r"C:\Users\blacklotus\bulk-wa\test.mp4"  # Use raw string for Windows paths

# Initialize the WebDriver (you'll need to set this up properly)
driver = webdriver.Chrome()  # or webdriver.Chrome() if you're using Chrome

# Set the window size to a common resolution
driver.set_window_size(1920, 1080)  # Set to a common resolution

# Send messages to each phone number
total_messages = len(phone_numbers)
successful_messages = 0

for phone_number in phone_numbers:
    if send_message(driver, phone_number, message, video_path):
        successful_messages += 1
    # Wait for 10 seconds between each message
    time.sleep(10)

logging.info(f"Total messages: {total_messages}")
logging.info(f"Successful messages: {successful_messages}")

# Don't forget to close the driver when you're done

