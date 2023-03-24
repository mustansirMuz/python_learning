import argparse
import json
import logging
import os
from datetime import datetime
from typing import List

from constants import app_constants, weather_api_constants
from dotenv import load_dotenv
from models import Base, CurrentWeather, ForecastWeather, Location
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from WeatherAPI import WeatherAPICurrent, WeatherAPIForecast

load_dotenv()


def get_db_engine() -> Engine:
    logging.info("Connecting to database...")
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    logging.info("Database Connected.")
    Base.metadata.create_all(engine)
    return engine


# Task 1


def save_forecast_data(location: str, interval: int) -> None:
    if not interval:
        interval = 1
    api = WeatherAPIForecast(os.getenv("WEATHER_API_KEY"))
    data = api.get_weather_data(location, days=interval)
    engine = get_db_engine()
    with Session(engine) as session:
        location_dict = data.get(app_constants.LOCATION, {})
        location = create_or_update_location(location_dict, session)
        for day in data.get(app_constants.FORECAST_DAYS, []):
            for hour in day.get(app_constants.HOURS, []):
                logging.info(
                    f"Saving forecast data for hour: {hour.get(app_constants.DATE_TIME)} location: {location.name} to DB."
                )
                create_or_update(
                    session,
                    ForecastWeather,
                    keys=["location", "date_time"],
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
                    cloud_cover_percent=hour.get(app_constants.CLOUD_COVER_PERCENT),
                    visibility_km=hour.get(app_constants.VISIBILITY_KM),
                    wind_gust_mph=hour.get(app_constants.GUST_MPH),
                    dew_point_c=hour.get(app_constants.DEWPOINT_C),
                    probability_of_rain_percent=hour.get(app_constants.CHANCE_OF_RAIN),
                    probability_of_snow_percent=hour.get(app_constants.CHANCE_OF_SNOW),
                    air_quality=hour.get(app_constants.AIR_QUALITY),
                )


# Task 2


def save_current_data(location: str) -> None:
    api = WeatherAPICurrent(os.getenv("WEATHER_API_KEY"))
    data = api.get_weather_data(location)
    engine = get_db_engine()
    with Session(engine) as session:
        location_dict = data.get(app_constants.LOCATION, {})
        location = create_or_update_location(location_dict, session)
        logging.info(f"Saving current data for location: {location.name} to DB.")
        create_or_update(
            session,
            CurrentWeather,
            keys=["location", "date_time"],
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


def create_or_update(session: Session, model, keys: List[str] = None, **kwargs):
    if keys:
        instance = (
            session.query(model)
            .filter_by(**dict([(k, v) for k, v in kwargs.items() if k in keys]))
            .first()
        )
    else:
        instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        for key, value in kwargs.items():
            setattr(instance, key, value)
    else:
        instance = model(**kwargs)
        session.add(instance)
    session.commit()
    return instance


def create_or_update_location(location_dict: dict, session: Session) -> Location:
    logging.info(
        f"Saving location: {location_dict.get(weather_api_constants.LOCATION_NAME)} to DB"
    )
    return create_or_update(
        session,
        Location,
        keys=["lat", "lon"],
        name=location_dict.get(weather_api_constants.LOCATION_NAME),
        region=location_dict.get(weather_api_constants.LOCATION_REGION),
        country=location_dict.get(weather_api_constants.LOCATION_COUNTRY),
        lat=location_dict.get(weather_api_constants.LOCATION_LAT),
        lon=location_dict.get(weather_api_constants.LOCATION_LON),
        tz_id=location_dict.get(weather_api_constants.LOCATION_TZ_ID),
    )


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
    parser.add_argument("--location", type=str, nargs="?", help="City or US zip code")
    parser.add_argument(
        "--interval", type=int, nargs="?", help="No of days to return forecast"
    )
    args = parser.parse_args()

    logging.info(
        "tasks.py: Requesting weather data with params: "
        + " ".join([f"{arg} = {getattr(args, arg)}," for arg in vars(args)])
    )
    if args.type == app_constants.CURRENT:
        save_current_data(args.location)
    elif args.type == app_constants.FORECAST:
        save_forecast_data(args.location, args.interval)
    else:
        logging.error("Invalid Type Parameter provided. Raising Exception")
        raise Exception("Invalid Type Param")
