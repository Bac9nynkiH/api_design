import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "secure"

RSA_KEY = ""

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def generate_joke(location: str, date: str):
    url_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url_api = "jokes"
    url_api_version = "v1"

    url = f"{url_base_url}/{location}/{date}?key={RSA_KEY}"

    headers = {"X-Api-Key": RSA_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = ""
    location = json_data.get("location")

    date = ""
    date = json_data.get("date")

    joke = generate_joke(location, date)

    end_dt = dt.datetime.now()

    dict = {
        "temp_c":joke["days"][0]["feelslike"],
        "wind_kph":joke["days"][0]["hours"][0]["windspeed"],
        "pressure_mb":joke["days"][0]["hours"][0]["pressure"],
        "humidity":joke["days"][0]["hours"][0]["humidity"]
    }

    result = {
        "requester_name": json_data.get("requester_name"),
        "timestamp": end_dt.isoformat(),
        "location": location,
        "date": date,
        "weather": dict
        
    }

    return result
