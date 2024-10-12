import pywhatkit
import openpyxl
import time
import logging
import re
import csv
import os
from datetime import datetime, date

# Configure logging
logging.basicConfig(filename='bulk_send_image.log', level=logging.INFO,
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

# Load the XLSX file
workbook = openpyxl.load_workbook('phone_numbers.xlsx')
sheet = workbook.active

# Read phone numbers from the XLSX file and format them
phone_numbers = [format_indonesian_number(cell.value) for cell in sheet['A'] if cell.value]

# Load already sent numbers
sent_numbers = load_sent_numbers()

# Promotional message and image path
message = "Hello! We are excited to offer you an exclusive deal on our latest products. Visit our website to learn more and take advantage of this limited-time offer.\n\nDon't miss out on our special discounts and promotions. Join our community today and stay updated with the latest news and offers!\n\nyynoes.me"
image_path = "test.png"

# Send messages to each phone number
total_messages = len(phone_numbers)
success_count = 0

start_time = time.time()

daily_count = load_daily_count()
daily_limit = 1000

for index, phone_number in enumerate(phone_numbers, start=1):
    if daily_count >= daily_limit:
        logging.info(f"Daily limit of {daily_limit} messages reached. Stopping for today.")
        break

    if phone_number in sent_numbers:
        logging.info(f"Skipping {phone_number} as it was already sent")
        continue

    try:
        # Send message with image
        message_start_time = time.time()
        pywhatkit.sendwhats_image(phone_number, image_path, message, 10, True, 2)
        message_end_time = time.time()
        
        # Calculate time taken for each message
        time_taken = message_end_time - message_start_time
        
        logging.info(f"Image message sent successfully to {phone_number}")
        logging.info(f"Time taken for message {index}: {time_taken:.2f} seconds")
        
        success_count += 1
        daily_count += 1
        
        # Save the sent number and update daily count
        save_sent_number(phone_number)
        save_daily_count(daily_count)
        
        # Delay between messages to avoid getting banned
        time.sleep(10)  # Adjust the delay as needed
        
    except Exception as e:
        logging.error(f"Failed to send image message to {phone_number}. Error: {str(e)}")

    # Check if we should pause and continue later
    if index % 50 == 0:
        user_input = input(f"Sent {index} image messages. Continue? (y/n): ")
        if user_input.lower() != 'y':
            logging.info(f"Paused after sending {index} image messages")
            break

end_time = time.time()
total_time = end_time - start_time

logging.info(f"Total messages: {total_messages}")
logging.info(f"Successful messages: {success_count}")
logging.info(f"Total time taken: {total_time:.2f} seconds")
logging.info(f"Average time per message: {total_time/total_messages:.2f} seconds")
