import argparse
import json
from datetime import datetime

import requests
from constants import app_constants, weather_api_constants


class WeatherAPI:
    """
    A base class that uses the WeatherAPI to fetch weather data.
    WeatherData's API key is required to initialize the WeatherAPI object.
    The abstract method get_weather_data is to be implemented to provide functionality for the specific endpoint.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/"

    def get_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        get_air_quality: bool = True,
        **kargs,
    ):
        raise NotImplementedError

    def display_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        get_air_quality: bool = True,
        **kwargs,
    ):
        """
        Displays weather data for the provided location. One of us_zip_code or city is required.
        Other params:
        - days: No of days to forecast (Only available for forecast API)
        - hour: hour to forecast for (Only available for forecast API)
        - get_air_quality - Boolean field to get air quality
        """
        print(
            json.dumps(
                self.get_weather_data(
                    us_zip_code=us_zip_code,
                    city=city,
                    get_air_quality=get_air_quality,
                    **kwargs,
                ),
                indent=4,
            )
        )

    def request_data(
        self,
        endpoint: str,
        us_zip_code: str,
        city: str,
        get_air_quality: bool,
        **kwargs,
    ) -> dict:
        """
        Requests data from the API based on given parameters and returns response as a dict.
        """
        if not us_zip_code and not city:
            raise Exception("us_zip_code or city is required.")

        return requests.get(
            f"{self.base_url}{endpoint}",
            params={
                "key": self.api_key,
                "q": us_zip_code if us_zip_code else city,
                "aqi": "yes" if get_air_quality else "no",
                **kwargs,
            },
        ).json()


class WeatherAPICurrent(WeatherAPI):
    def get_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        get_air_quality: bool = True,
    ) -> dict:
        """
        Returns the current data for the provided location. One of us_zip_code or city is required.
        Other params:
        get_air_quality - Boolean field to get air quality
        """
        data = self.request_data(
            "current.json",
            us_zip_code=us_zip_code,
            city=city,
            get_air_quality=get_air_quality,
        )

        current = data.get(weather_api_constants.CURRENT, {})
        response = {
            app_constants.LOCATION: data.get(weather_api_constants.LOCATION),
            app_constants.DATE_TIME: Utils.format_datetime(
                data.get(weather_api_constants.LOCATION, {}).get(
                    weather_api_constants.LOCATION_LOCALTIME
                )
            ),
            app_constants.TEMP_C: current.get(weather_api_constants.TEMP_C),
            app_constants.CONDITION: current.get(
                weather_api_constants.CONDITION, {}
            ).get(weather_api_constants.CONDITION_TEXT),
            app_constants.FEELSLIKE_C: current.get(weather_api_constants.FEELSLIKE_C),
            app_constants.WIND_MPH: current.get(weather_api_constants.WIND_MPH),
            app_constants.HUMIDITY_PERCENT: current.get(
                weather_api_constants.HUMIDITY_PERCENT
            ),
            app_constants.WIND_PRESSURE_IN: current.get(
                weather_api_constants.WIND_PRESSURE_IN
            ),
            app_constants.CLOUD_COVER_PERCENT: current.get(
                weather_api_constants.CLOUD_COVER_PERCENT
            ),
            app_constants.VISIBILITY_KM: current.get(
                weather_api_constants.VISIBILITY_KM
            ),
        }
        if get_air_quality:
            response[app_constants.AIR_QUALITY] = Utils.get_air_quality(
                current.get(weather_api_constants.AIR_QUALITY, {}).get(
                    weather_api_constants.PM2_5
                )
            )
        return response


class WeatherAPIForecast(WeatherAPI):
    def get_weather_data(
        self,
        us_zip_code: str = None,
        city: str = None,
        days: int = None,
        hour: int = None,
        get_air_quality: bool = True,
    ) -> dict:
        """
        Returns the forecast data for the provided location. One of us_zip_code or city is required.
        Other params:
        days - No of days to get forecast for
        hour - Hour to get forecast for
        get_air_quality - Boolean field to get air quality
        """
        data = self.request_data(
            "forecast.json",
            us_zip_code,
            city,
            days=days,
            hour=hour,
            get_air_quality=get_air_quality,
        )
        response = {
            app_constants.LOCATION: data.get(weather_api_constants.LOCATION),
            app_constants.FORECAST_DAYS: [],
        }
        for forecastday in data.get(weather_api_constants.FORECAST, {}).get(
            weather_api_constants.FORECAST_DAY, []
        ):
            day = forecastday.get(weather_api_constants.DAY, {})
            day_dict = {
                app_constants.FORECAST_DATE: forecastday.get(
                    weather_api_constants.FORECAST_DATE
                ),
                app_constants.MAX_TEMP_C: day.get(weather_api_constants.MAX_TEMP_C),
                app_constants.MIN_TEMP_C: day.get(weather_api_constants.MIN_TEMP_C),
                app_constants.CONDITION: day.get(
                    weather_api_constants.CONDITION, {}
                ).get(weather_api_constants.CONDITION_TEXT),
                app_constants.MAX_WIND_MPH: day.get(weather_api_constants.MAX_WIND_MPH),
                app_constants.HUMIDITY_PERCENT: day.get(
                    weather_api_constants.AVG_HUMIDITY_PERCENT
                ),
                app_constants.VISIBILITY_KM: day.get(
                    weather_api_constants.AVG_VISIBILITY_KM
                ),
                app_constants.CHANCE_OF_RAIN: day.get(
                    weather_api_constants.DAILY_CHANCE_OF_RAIN
                ),
                app_constants.CHANCE_OF_SNOW: day.get(
                    weather_api_constants.DAILY_CHANCE_OF_SNOW
                ),
            }
            if get_air_quality:
                day_dict[app_constants.AIR_QUALITY] = Utils.get_air_quality(
                    day.get(weather_api_constants.AIR_QUALITY, {}).get(
                        weather_api_constants.PM2_5
                    )
                )

            day_dict[app_constants.HOURS] = []

            for hour in forecastday.get(weather_api_constants.HOUR, []):
                hour_dict = {
                    app_constants.DATE_TIME: Utils.format_datetime(
                        hour.get(weather_api_constants.TIME)
                    ),
                    app_constants.TEMP_C: hour.get(weather_api_constants.TEMP_C),
                    app_constants.CONDITION: hour.get(
                        weather_api_constants.CONDITION, {}
                    ).get(weather_api_constants.CONDITION_TEXT),
                    app_constants.FEELSLIKE_C: hour.get(
                        weather_api_constants.FEELSLIKE_C
                    ),
                    app_constants.WIND_MPH: hour.get(weather_api_constants.WIND_MPH),
                    app_constants.HUMIDITY_PERCENT: hour.get(
                        weather_api_constants.HUMIDITY_PERCENT
                    ),
                    app_constants.WIND_PRESSURE_IN: hour.get(
                        weather_api_constants.WIND_PRESSURE_IN
                    ),
                    app_constants.GUST_MPH: hour.get(weather_api_constants.GUST_MPH),
                    app_constants.CLOUD_COVER_PERCENT: hour.get(
                        weather_api_constants.CLOUD_COVER_PERCENT
                    ),
                    app_constants.VISIBILITY_KM: hour.get(
                        weather_api_constants.VISIBILITY_KM
                    ),
                    app_constants.DEWPOINT_C: hour.get(
                        weather_api_constants.DEWPOINT_C
                    ),
                    app_constants.CHANCE_OF_RAIN: hour.get(
                        weather_api_constants.CHANCE_OF_RAIN
                    ),
                    app_constants.CHANCE_OF_SNOW: hour.get(
                        weather_api_constants.CHANCE_OF_SNOW
                    ),
                }
                if get_air_quality:
                    hour_dict[app_constants.AIR_QUALITY] = Utils.get_air_quality(
                        hour.get(weather_api_constants.AIR_QUALITY, {}).get(
                            weather_api_constants.PM2_5
                        )
                    )

                day_dict[app_constants.HOURS].append(hour_dict)

            response[app_constants.FORECAST_DAYS].append(day_dict)
        return response


class Utils:
    def get_air_quality(pm2_5: float) -> str | None:
        """
        A helper function to get air quality based on pm2.5 value provided.
        """
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

    def format_datetime(date_time: str) -> str:
        """
        Formats the datetime sent from the API.
        """
        if date_time:
            date_time = datetime.strptime(
                date_time, weather_api_constants.DATE_TIME_FORMAT
            ).strftime(app_constants.DATE_TIME_FORMAT)
        return date_time
