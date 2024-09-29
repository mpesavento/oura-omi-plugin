import os
from datetime import datetime, timedelta
import json
import logging
import pytz

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
    try:
        selected_date = request.form.get('selected_date')
        user_timezone = request.headers.get('X-User-Timezone')

        logging.info(f"Selected date: {selected_date}, User timezone: {user_timezone}")

        # Convert to datetime object in user's timezone
        user_tz = pytz.timezone(user_timezone)
        date_obj = user_tz.localize(datetime.strptime(selected_date, '%Y-%m-%d'))

        # Get the next day for the API call
        next_day = date_obj + timedelta(days=1)

        # Add an extra day for heart rate data
        extra_day = next_day + timedelta(days=1)

        # Convert to UTC for API calls
        utc_start = date_obj.astimezone(pytz.UTC)
        utc_end = next_day.astimezone(pytz.UTC)
        utc_extra_end = extra_day.astimezone(pytz.UTC)

        # Format dates as 'YYYY-MM-DD' strings for Oura API
        start_date = utc_start.date().isoformat()
        end_date = utc_end.date().isoformat()
        extra_end_date = utc_extra_end.date().isoformat()

        sleep_data = oura_client.get_daily_sleep(start_date, end_date)
        activity_data = oura_client.get_daily_activity(start_date, end_date)
        readiness_data = oura_client.get_daily_readiness(start_date, end_date)
        heart_rate_data = oura_client.get_heart_rate(start_date, extra_end_date)  # Use extra_end_date for heart rate
        # heart_rate_data = oura_client.get_heart_rate(start_date, end_date)  # Use extra_end_date for heart rate
        sleep_time_data = oura_client.get_sleep_time(start_date, end_date)

        # Extract sleep period for shading
        sleep_periods = oura_client.get_sleep_periods(start_date, end_date)
        sleep_period = sleep_periods[-1] if sleep_periods else None

        data = {
            'sleep': sleep_data[0] if sleep_data else None,
            'activity': activity_data[0] if activity_data else None,
            'readiness': readiness_data[0] if readiness_data else None,
            'heartRate': heart_rate_data,
            'sleepTime': sleep_time_data,
            'sleepPeriods': sleep_periods,
            'sleepPeriod': {
                'bedtime_start': sleep_period['bedtime_start'] if sleep_period else None,
                'bedtime_end': sleep_period['bedtime_end'] if sleep_period else None
            }
        }

        return jsonify(data)

    except Exception as e:
        logging.exception("An error occurred in get_oura_data:")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    # DEBUG=True
    app.run(debug=DEBUG)
