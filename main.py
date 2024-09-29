import os
from datetime import datetime, timedelta
import json
import logging

import dotenv
from openai import OpenAI

from flask import Flask, render_template, request, jsonify

from oura_client.oura_ring import OuraClient

dotenv.load_dotenv()

OURA_PERSONAL_TOKEN = os.getenv("OURA_PERSONAL_TOKEN")
oura_client = OuraClient(OURA_PERSONAL_TOKEN)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

@app.route('/')
def index():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html',
                           current_date=current_date
                        )


@app.route('/api/get_oura_data', methods=['POST'])
def get_oura_data():
    selected_date = request.form.get('selected_date')

    logging.info(f"Selected date: {selected_date}")

    # Convert to datetime object
    date_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Get the next day for the API call
    next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

    sleep_data = oura_client.get_daily_sleep(selected_date, next_day)
    activity_data = oura_client.get_daily_activity(selected_date, next_day)
    readiness_data = oura_client.get_daily_readiness(selected_date, next_day)
    heart_rate_data = oura_client.get_heart_rate(f"{selected_date}T00:00:00", f"{next_day}T00:00:00")

    # Extract sleep period for shading
    sleep_periods = oura_client.get_sleep_periods(selected_date, next_day)
    sleep_period = sleep_periods[0] if sleep_periods else None

    data = {
        'sleep': sleep_data[0] if sleep_data else None,
        'activity': activity_data[0] if activity_data else None,
        'readiness': readiness_data[0] if readiness_data else None,
        'heartRate': heart_rate_data,
        'sleepPeriod': {
            'bedtime_start': sleep_period['bedtime_start'] if sleep_period else None,
            'bedtime_end': sleep_period['bedtime_end'] if sleep_period else None
        }
    }

    return jsonify(data)



if __name__ == '__main__':

    # DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DEBUG=True
    app.run(debug=DEBUG)
