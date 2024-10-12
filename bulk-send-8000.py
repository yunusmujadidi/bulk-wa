import pywhatkit
import openpyxl
import time
import logging

# Configure logging
logging.basicConfig(filename='bulk_send.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load the XLSX file
workbook = openpyxl.load_workbook('phone_numbers.xlsx')
sheet = workbook.active

# Read phone numbers from the XLSX file
phone_numbers = [cell.value for cell in sheet['A']]

# Promotional message and image path
message = "Halo! Ini adalah pesan promosi dari kami. Jangan lewatkan penawaran spesial kami!"
image_path = "The Ritz Carlton Maldives.png"

# Send messages to each phone number
total_messages = len(phone_numbers)
success_count = 0
skipped_count = 0

start_time = time.time()

for index, phone_number in enumerate(phone_numbers, start=1):
    try:
        # Check if the phone number has a WhatsApp account
        if pywhatkit.check_number(phone_number):
            # Send message with image
            pywhatkit.sendwhats_image(phone_number, image_path, message, 15, True, 3)
            success_count += 1
        else:
            skipped_count += 1
        
        # Log progress every 100 messages
        if index % 100 == 0:
            logging.info(f"Processed {index} out of {total_messages} messages")
        
        # Delay between messages to avoid getting banned
        time.sleep(5)  # Adjust the delay as needed
        
    except Exception as e:
        logging.error(f"Failed to send message to {phone_number}. Error: {str(e)}")

end_time = time.time()

# Calculate total time taken and average time per message
total_time = end_time - start_time
avg_time_per_message = total_time / total_messages

logging.info(f"Total messages: {total_messages}")
logging.info(f"Successful messages: {success_count}")
logging.info(f"Skipped messages: {skipped_count}")
logging.info(f"Total time taken: {total_time:.2f} seconds")
logging.info(f"Average time per message: {avg_time_per_message:.2f} seconds")