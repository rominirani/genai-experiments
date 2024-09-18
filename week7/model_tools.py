import requests, json
import pandas as pd

def get_location_data(location_name:str):
  """Retrieves location data from the Open-Meteo Geocoding API.

  This function takes a location name as input and returns
  a JSON object containing location data from the Open-Meteo API.

  Args:
    location_name: The name of the location to search for. eg. "Mumbai, India"

  Returns:
    A JSON object containing location data.
  """

  location_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=10&language=en&format=json"
  response = requests.get(location_url)
  response_json = json.loads(response.text)
  return response_json


def get_weather_forecast(latitude:str, longitude:str, timezone:str = "Asia/Kolkata", forecast_days:int = 3):
  """Retrieves weather forecast data from the Open-Meteo Weather API.

  This function takes latitude, longitude, timezone, and forecast days as input,
  and returns a json object containing the weather forecast data.

  Args:
      latitude: The latitude of the location.
      longitude: The longitude of the location.
      timezone: The timezone of the location (default: "Asia/Kolkata").
      forecast_days: The number of forecast days (default: 3).

  Returns:
      A Json object containing the weather forecast data.
  """


  weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&timezone={timezone}&forecast_days={forecast_days}"
  response = requests.get(weather_url)
  response_json = json.loads(response.text)

  # Basic Transformation of results
  df = pd.DataFrame()
  df["DateTime"] = response_json["hourly"]["time"]
  df["Temperatura"] = response_json["hourly"]["temperature_2m"]

  return df.to_json(orient="records")