import argparse
import json
import logging
import os
from datetime import datetime

from constants import app_constants, weather_api_constants
from dotenv import load_dotenv
from models import (
    Base,
    CurrentWeather,
    ForecastWeatherDay,
    ForecastWeatherHour,
    Location,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from WeatherAPI import WeatherAPICurrent, WeatherAPIForecast

load_dotenv()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


if __name__ == "__main__":
    if not os.path.isdir(os.getenv("LOG_DIR")):
        os.mkdir(os.getenv("LOG_DIR"))
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        filename=f"{os.getenv('LOG_DIR')}/{datetime.now().strftime('%Y%m%d')}.txt",
        filemode="a",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        prog="Weather API",
    )
    parser.add_argument(
        "--type",
        type=str,
        nargs="?",
        help=f"Type of API call ({app_constants.CURRENT}/{app_constants.FORECAST})",
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
    parser.add_argument(
        "--display_only",
        action=argparse.BooleanOptionalAction,
        help="Only display the data. Do not save to DB",
    )
    args = parser.parse_args()

    logging.info(
        "Requesting weather data with params: "
        + " ".join([f"{arg} = {getattr(args, arg)}," for arg in vars(args)])
    )
    if args.type == app_constants.CURRENT:
        api = WeatherAPICurrent(os.getenv("WEATHER_API_KEY"))
        data = api.get_weather_data(
            us_zip_code=args.us_zip,
            city=args.city,
            get_air_quality=args.get_aqi,
        )
    elif args.type == app_constants.FORECAST:
        api = WeatherAPIForecast(os.getenv("WEATHER_API_KEY"))
        data = api.get_weather_data(
            us_zip_code=args.us_zip,
            city=args.city,
            get_air_quality=args.get_aqi,
            days=args.days,
            hour=args.hour,
        )
    else:
        logging.error("Invalid Type Parameter provided. Raising Exception")
        raise Exception("Invalid Type Param")

    print(json.dumps(data, indent=4))

    if not args.display_only:
        logging.info("Connecting to database...")
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        logging.info("Database Connected.")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            location_dict = data.get(app_constants.LOCATION, {})
            logging.info(
                f"Saving location: {location_dict.get(weather_api_constants.LOCATION_NAME)} to DB"
            )
            location = get_or_create(
                session,
                Location,
                name=location_dict.get(weather_api_constants.LOCATION_NAME),
                region=location_dict.get(weather_api_constants.LOCATION_REGION),
                country=location_dict.get(weather_api_constants.LOCATION_COUNTRY),
                lat=location_dict.get(weather_api_constants.LOCATION_LAT),
                lon=location_dict.get(weather_api_constants.LOCATION_LON),
                tz_id=location_dict.get(weather_api_constants.LOCATION_TZ_ID),
            )
            logging.info(f"Saving weather data of type {app_constants.CURRENT} to DB")
            if args.type == app_constants.CURRENT:
                get_or_create(
                    session,
                    CurrentWeather,
                    location=location,
                    date_time=datetime.strptime(
                        data.get(app_constants.DATE_TIME),
                        app_constants.DATE_TIME_FORMAT,
                    ),
                    temp_c=data.get(app_constants.TEMP_C),
                    condition=data.get(app_constants.CONDITION),
                    realfeel_c=data.get(app_constants.FEELSLIKE_C),
                    wind_speed_mph=data.get(app_constants.WIND_MPH),
                    humidity_percent=data.get(app_constants.HUMIDITY_PERCENT),
                    wind_pressure_in=data.get(app_constants.WIND_PRESSURE_IN),
                    cloud_cover_percent=data.get(app_constants.CLOUD_COVER_PERCENT),
                    visibility_km=data.get(app_constants.VISIBILITY_KM),
                    air_quality=data.get(app_constants.AIR_QUALITY),
                )
            else:
                for day in data.get(app_constants.FORECAST_DAYS, []):
                    get_or_create(
                        session,
                        ForecastWeatherDay,
                        location=location,
                        date_time=datetime.strptime(
                            day.get(app_constants.FORECAST_DATE),
                            app_constants.DATE_FORMAT,
                        ),
                        max_temp_c=day.get(app_constants.MAX_TEMP_C),
                        min_temp_c=day.get(app_constants.MIN_TEMP_C),
                        condition=day.get(app_constants.CONDITION),
                        max_wind_mph=day.get(app_constants.MAX_WIND_MPH),
                        humidity_percent=day.get(app_constants.HUMIDITY_PERCENT),
                        visibility_km=day.get(app_constants.VISIBILITY_KM),
                        probability_of_rain_percent=day.get(
                            app_constants.CHANCE_OF_RAIN
                        ),
                        probability_of_snow_percent=day.get(
                            app_constants.CHANCE_OF_SNOW
                        ),
                        air_quality=day.get(app_constants.AIR_QUALITY),
                    )
                    for hour in day.get(app_constants.HOURS, []):
                        get_or_create(
                            session,
                            ForecastWeatherHour,
                            location=location,
                            date_time=datetime.strptime(
                                hour.get(app_constants.DATE_TIME),
                                app_constants.DATE_TIME_FORMAT,
                            ),
                            temp_c=hour.get(app_constants.TEMP_C),
                            condition=hour.get(app_constants.CONDITION),
                            realfeel_c=hour.get(app_constants.FEELSLIKE_C),
                            wind_speed_mph=hour.get(app_constants.WIND_MPH),
                            humidity_percent=hour.get(app_constants.HUMIDITY_PERCENT),
                            wind_pressure_in=hour.get(app_constants.WIND_PRESSURE_IN),
                            cloud_cover_percent=hour.get(
                                app_constants.CLOUD_COVER_PERCENT
                            ),
                            visibility_km=hour.get(app_constants.VISIBILITY_KM),
                            wind_gust_mph=hour.get(app_constants.GUST_MPH),
                            dew_point_c=hour.get(app_constants.DEWPOINT_C),
                            probability_of_rain_percent=hour.get(
                                app_constants.CHANCE_OF_RAIN
                            ),
                            probability_of_snow_percent=hour.get(
                                app_constants.CHANCE_OF_SNOW
                            ),
                            air_quality=hour.get(app_constants.AIR_QUALITY),
                        )
