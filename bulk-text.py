import pywhatkit
import openpyxl
import time
import logging
import re

# Configure logging
logging.basicConfig(filename='bulk_send_text.log', level=logging.INFO,
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

# Load the XLSX file
workbook = openpyxl.load_workbook('phone_numbers.xlsx')
sheet = workbook.active

# Read phone numbers from the XLSX file and format them
phone_numbers = [format_indonesian_number(cell.value) for cell in sheet['A'] if cell.value]

# Promotional message
message = """Hello! We are excited to share our latest products with you.

Don't miss out on our special discounts and promotions. Join our community today and stay updated with the latest news and offers!

Visit us at: yynoes.me"""

# Send messages to each phone number
total_messages = len(phone_numbers)
success_count = 0

start_time = time.time()

for index, phone_number in enumerate(phone_numbers, start=1):
    try:
        # Send text message
        message_start_time = time.time()
        pywhatkit.sendwhatmsg_instantly(phone_number, message, 15, True, 3)
        message_end_time = time.time()
        
        # Calculate time taken for each message
        time_taken = message_end_time - message_start_time
        
        logging.info(f"Text message sent successfully to {phone_number}")
        logging.info(f"Time taken for message {index}: {time_taken:.2f} seconds")
        
        success_count += 1
        
        # Delay between messages to avoid getting banned
        time.sleep(5)  # Reduced delay for text-only messages
        
    except Exception as e:
        logging.error(f"Failed to send text message to {phone_number}. Error: {str(e)}")

end_time = time.time()
total_time = end_time - start_time

logging.info(f"Total messages: {total_messages}")
logging.info(f"Successful messages: {success_count}")
logging.info(f"Total time taken: {total_time:.2f} seconds")
logging.info(f"Average time per message: {total_time/total_messages:.2f} seconds")