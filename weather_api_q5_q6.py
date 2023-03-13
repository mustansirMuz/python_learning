import argparse
import json
from datetime import datetime

import requests


class WeatherAPI:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/"

    def get_current_weather_data(
        self, us_zip_code: str = None, city: str = None, get_air_quality: bool = True
    ) -> dict:
        data = self.request_data(
            "current.json",
            us_zip_code,
            city,
            days=None,
            hour=None,
            get_air_quality=get_air_quality,
        )

        current = data.get("current", {})
        response = {
            "Location": data.get("location"),
            "Current Date/Time": self.format_datetime(
                data.get("location", {}).get("localtime")
            ),
            "Temperature (C)": current.get("temp_c"),
            "Condition": current.get("condition", {}).get("text"),
            "RealFeel (C)": current.get("feelslike_c"),
            "Wind Speed (mph)": current.get("wind_mph"),
            "Humidity %": current.get("humidity"),
            "Wind Pressure (in)": current.get("pressure_in"),
            "Cloud Cover (%)": current.get("cloud"),
            "Visibility (km)": current.get("vis_km"),
        }
        if get_air_quality:
            response["Air Quality"] = self.get_air_quality(
                current.get("air_quality", {}).get("pm2_5")
            )
        return response

    def display_current_weather_data(
        self, us_zip_code: str = None, city: str = None, get_air_quality: bool = True
    ) -> None:
        print(
            json.dumps(
                self.get_current_weather_data(us_zip_code, city, get_air_quality),
                indent=4,
            )
        )

    def get_forecast_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        days: int = None,
        hour: int = None,
        get_air_quality: bool = True,
    ) -> dict:
        data = self.request_data(
            "forecast.json",
            us_zip_code,
            city,
            days=days,
            hour=hour,
            get_air_quality=get_air_quality,
        )
        response = {"Location": data.get("location"), "Forecast Days": []}
        for forecastday in data.get("forecast", {}).get("forecastday", []):
            day = forecastday.get("day", {})
            day_dict = {
                "Date": forecastday.get("date"),
                "Max Temp (C)": day.get("maxtemp_c"),
                "Min Temp (C)": day.get("mintemp_c"),
                "Condition": day.get("condition", {}).get("text"),
                "Max Wind (mph)": day.get("maxwind_mph"),
                "Humidity (%)": day.get("avghumidity"),
                "Visibility (km)": day.get("avgvis_km"),
                "Probability of Rain (%)": day.get("daily_chance_of_rain"),
                "Probability of Snow (%)": day.get("daily_chance_of_snow"),
            }
            if get_air_quality:
                day_dict["Air Quality"] = self.get_air_quality(
                    day.get("air_quality", {}).get("pm2_5")
                )

            day_dict["Hours"] = []

            for hour in forecastday.get("hour", []):
                hour_dict = {
                    "Date/Time": self.format_datetime(hour.get("time")),
                    "Temperature (C)": hour.get("temp_c"),
                    "Condition": hour.get("condition", {}).get("text"),
                    "RealFeel (C)": hour.get("feelslike_c"),
                    "Wind Speed (mph)": hour.get("wind_mph"),
                    "Humidity %": hour.get("humidity"),
                    "Wind Pressure (in)": hour.get("pressure_in"),
                    "Wind Gust (mph)": hour.get("gust_mph"),
                    "Cloud Cover (%)": hour.get("cloud"),
                    "Visibility (km)": hour.get("vis_km"),
                    "Dew Point (C)": hour.get("dewpoint_c"),
                    "Probability of Rain (%)": hour.get("chance_of_rain"),
                    "Probability of Snow (%)": hour.get("chance_of_snow"),
                }
                if get_air_quality:
                    hour_dict["Air Quality"] = self.get_air_quality(
                        hour.get("air_quality", {}).get("pm2_5")
                    )

                day_dict["Hours"].append(hour_dict)

            response["Forecast Days"].append(day_dict)
        return response

    def display_forecast_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        days: int = None,
        hour: int = None,
        get_air_quality: bool = True,
    ) -> None:
        print(
            json.dumps(
                self.get_forecast_weather_data(
                    us_zip_code, city, days, hour, get_air_quality
                ),
                indent=4,
            )
        )

    def get_air_quality(self, pm2_5: float) -> str | None:
        if pm2_5 is None:
            return None
        if pm2_5 > 250:
            return "Severe"
        if pm2_5 > 120:
            return "Very poor"
        if pm2_5 > 90:
            return "Poor"
        if pm2_5 > 60:
            return "Moderate"
        if pm2_5 > 30:
            return "Satisfactory"
        return "Good"

    def request_data(
        self,
        endpoint: str,
        us_zip_code: str,
        city: str,
        days: int,
        hour: int,
        get_air_quality: bool,
    ) -> dict:
        if not us_zip_code and not city:
            raise Exception("us_zip_code or city is required.")

        return requests.get(
            f"{self.base_url}{endpoint}",
            params={
                "key": self.api_key,
                "q": us_zip_code if us_zip_code else city,
                "aqi": "yes" if get_air_quality else "no",
                "days": days,
                "hour": hour,
            },
        ).json()

    def format_datetime(self, date_time):
        if date_time:
            date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M").strftime(
                "%Y-%m-%d %I:%M %p"
            )
        return date_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Weather API",
    )
    parser.add_argument(
        "--type", type=str, nargs="?", help="Type of API call (current/forecast)"
    )
    parser.add_argument("--us_zip", type=str, nargs="?", help="US zip code")
    parser.add_argument("--city", type=str, nargs="?", help="City")
    parser.add_argument(
        "--get_aqi", action=argparse.BooleanOptionalAction, help="Get Air Quality"
    )
    parser.add_argument(
        "--days", type=int, nargs="?", help="No of days to return forecast"
    )
    parser.add_argument(
        "--hour", type=int, nargs="?", help="Hour to return forecast for (0-23)"
    )

    args = parser.parse_args()

    api = WeatherAPI("e38e088af196452e88f145935230903")

    if args.type == "current":
        api.display_current_weather_data(
            us_zip_code=args.us_zip, city=args.city, get_air_quality=args.get_aqi
        )
    elif args.type == "forecast":
        api.display_forecast_weather_data(
            us_zip_code=args.us_zip,
            city=args.city,
            days=args.days,
            hour=args.hour,
            get_air_quality=args.get_aqi,
        )
    else:
        raise Exception("Invalid Type!")
