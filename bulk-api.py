import requests
import json
import time
import base64
import csv
import os
from datetime import datetime, date

# Interakt API credentials
api_key = "YOUR_API_KEY"
api_url = "https://api.interakt.ai/v1/public/message/"

def load_sent_numbers():
    sent_numbers = set()
    if os.path.exists('sent_numbers_api.csv'):
        with open('sent_numbers_api.csv', 'r') as f:
            reader = csv.reader(f)
            sent_numbers = set(row[0] for row in reader)
    return sent_numbers

def save_sent_number(phone_number):
    with open('sent_numbers_api.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([phone_number])

def load_daily_count():
    if os.path.exists('daily_count_api.csv'):
        with open('daily_count_api.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    last_date, count = row
                    if last_date == str(date.today()):
                        return int(count)
    return 0

def save_daily_count(count):
    with open('daily_count_api.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([str(date.today()), count])

# Load phone numbers from the file
with open("phone_numbers.txt", "r") as file:
    phone_numbers = file.read().splitlines()

# Load already sent numbers
sent_numbers = load_sent_numbers()

# Video file path
video_path = "test.mp4"

# Read and encode the video file
with open(video_path, "rb") as video_file:
    video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

# Video caption
caption = "Check out our latest video!"

# Send messages to each phone number
total_messages = len(phone_numbers)
success_count = 0

daily_count = load_daily_count()
daily_limit = 1000

start_time = time.time()

for index, phone_number in enumerate(phone_numbers, start=1):
    if daily_count >= daily_limit:
        print(f"Daily limit of {daily_limit} messages reached. Stopping for today.")
        break

    if phone_number in sent_numbers:
        print(f"Skipping {phone_number} as it was already sent")
        continue

    try:
        # Prepare the request payload
        payload = {
            "countryCode": "62",  # Indonesia country code
            "phoneNumber": phone_number,
            "callbackData": "some_data",
            "type": "Video",
            "video": {
                "url": f"data:video/mp4;base64,{video_base64}",
                "caption": caption
            }
        }

        # Send the message using Interakt API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {api_key}"
        }
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            success_count += 1
            daily_count += 1
            print(f"Video sent successfully to {phone_number}")
            save_sent_number(phone_number)
            save_daily_count(daily_count)
        else:
            print(f"Failed to send video to {phone_number}. Status code: {response.status_code}")

        # Delay between messages to avoid hitting rate limits
        time.sleep(1)

    except Exception as e:
        print(f"Failed to send video to {phone_number}. Error: {str(e)}")

    # Check if we should pause and continue later
    if index % 100 == 0:
        user_input = input(f"Sent {index} video messages. Continue? (y/n): ")
        if user_input.lower() != 'y':
            print(f"Paused after sending {index} video messages")
            break

end_time = time.time()
total_time = end_time - start_time

print(f"Total messages: {total_messages}")
print(f"Successful messages: {success_count}")
print(f"Total time taken: {total_time:.2f} seconds")
print(f"Average time per message: {total_time/total_messages:.2f} seconds")
