from flask import Flask, request, jsonify
import threading
import csv
import json
import requests
import random
import time
from datetime import datetime

app = Flask(__name__)

def send_data_to_webhook(first_name, last_name, email, linkedin_profile, company_name, webhook_url, session_cookies, user_agent):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "linkedin_profile": linkedin_profile,
        "company_name": company_name,
        "session_cookies": session_cookies,
        "User-Agent": user_agent
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print(f"Data sent successfully to the webhook. LinkedIn Profile: {linkedin_profile}")
        else:
            print(f"Failed to send data to the webhook. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending data to the webhook: {e}")

def main(csv_filename, webhook_url, session_cookies, user_agent):
    with open(csv_filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            first_name = row.get('first_name')
            last_name = row.get('last_name')
            email = row.get('email')
            linkedin_profile = row.get('linkedin_profile')
            company_name = row.get('company_name')

            current_time = datetime.utcnow()
            if current_time.hour < 8 or current_time.hour >= 17:
                print("Skipping sending data outside of the allowed time window.")
                continue

            try:
                send_data_to_webhook(first_name, last_name, email, linkedin_profile, company_name, webhook_url, session_cookies, user_agent)
            except Exception as e:
                print("An error occurred while sending data from row:", e)

            delay_minutes = random.randint(5, 15)
            print(f"Waiting for {delay_minutes} minutes before sending the next row.")
            time.sleep(delay_minutes * 60)

@app.route('/start-script', methods=['POST'])
def start_script():
    data = request.get_json()
    csv_filename = data.get('csv_filename')
    webhook_url = data.get('webhook_url')
    session_cookies = data.get('session_cookies')
    user_agent = data.get('user_agent')

    if not all([csv_filename, webhook_url, session_cookies, user_agent]):
        return jsonify({'error': 'Missing required parameters'}), 400

    thread = threading.Thread(target=main, args=(csv_filename, webhook_url, session_cookies, user_agent))
    thread.start()

    return jsonify({'message': 'Script is running'}), 202

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
