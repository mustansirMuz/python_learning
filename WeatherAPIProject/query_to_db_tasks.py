import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List

from constants import app_constants, weather_api_constants
from dotenv import load_dotenv
from models import Base, CurrentWeather, ForecastWeather, Location
from saving_to_db_tasks import save_forecast_data
from sqlalchemy import Engine, create_engine, desc, func, text
from sqlalchemy.orm import Session
from WeatherAPI import WeatherAPICurrent, WeatherAPIForecast

load_dotenv()

if not os.path.isdir(os.getenv("LOG_DIR")):
    os.mkdir(os.getenv("LOG_DIR"))
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    filename=f"{os.getenv('LOG_DIR')}/{datetime.now().strftime('%Y%m%d')}.txt",
    filemode="a",
    level=logging.INFO,
)

# some helper functions


def get_db_engine() -> Engine:
    logging.info("Connecting to database...")
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    logging.info("Database Connected.")
    Base.metadata.create_all(engine)
    return engine


def fetch_data_if_not_present_in_db(
    session: Session, days: int, location: Location | str
) -> Location:
    end_date = datetime.now() + timedelta(days=days)
    if type(location) == str:
        save_forecast_data(location, days)
        location = get_location(location, session)
    else:
        latest_hour = (
            session.query(ForecastWeather)
            .filter(ForecastWeather.location == location)
            .order_by(desc(ForecastWeather.date_time))
            .first()
        )
        if not latest_hour or latest_hour.date_time.date() < end_date.date():
            save_forecast_data(location.name, days)
    return location


def get_location(city: str, session: Session) -> Location:
    return (
        session.query(Location)
        .filter(func.lower(Location.name) == func.lower(city))
        .first()
    )


def check_valid_days(days: int) -> None:
    if type(days) != int or days <= 0:
        raise Exception("Invalid days")


# Task 1


def get_hottest_day(city: str, days: int) -> dict:
    check_valid_days(days)
    engine = get_db_engine()
    with Session(engine) as session:
        end_date = datetime.now() + timedelta(days=days)
        location = get_location(city, session)
        if not location:
            location = city
        location = fetch_data_if_not_present_in_db(session, days, location)
        hottest_hour = (
            session.query(ForecastWeather)
            .filter(
                ForecastWeather.location == location,
                ForecastWeather.date_time >= datetime.now(),
                ForecastWeather.date_time <= end_date,
            )
            .order_by(desc(ForecastWeather.temp_c))
            .first()
        )
        return {
            "highest_peak_temp_datetime": str(hottest_hour.date_time),
            "highest_peak_temp": hottest_hour.temp_c,
        }


# Task 2


def get_second_most_humid_city() -> dict:
    engine = get_db_engine()
    with Session(engine) as session:
        locations = session.query(Location).all()
        for location in locations:
            fetch_data_if_not_present_in_db(session, 7, location)

        end_date = datetime.now() + timedelta(days=7)
        second_most_humid_day = (
            session.query(
                ForecastWeather.location_id, func.avg(ForecastWeather.humidity_percent)
            )
            .filter(
                ForecastWeather.date_time >= datetime.now(),
                ForecastWeather.date_time <= end_date,
            )
            .group_by(ForecastWeather.location_id)
            .order_by(desc(func.avg(ForecastWeather.humidity_percent)))
            .all()[1]
        )
        return {
            "second_most_humid_city": session.query(Location)
            .filter(Location.id == second_most_humid_day[0])
            .first()
            .name,
            "humidity_percent": round(second_most_humid_day[1], 2),
        }


# Task 3


def get_lowest_average_daily_temp_difference(days: int) -> dict:
    check_valid_days(days)
    engine = get_db_engine()
    with Session(engine) as session:
        locations = session.query(Location).all()
        for location in locations:
            fetch_data_if_not_present_in_db(session, days, location)

        end_date = datetime.now() + timedelta(days=days)

        # Calculate the daily temperature difference for the next n days
        sub_query = (
            session.query(
                ForecastWeather.location_id,
                (
                    func.max(ForecastWeather.temp_c) - func.min(ForecastWeather.temp_c)
                ).label("temp_difference"),
            )
            .filter(
                ForecastWeather.date_time >= datetime.now(),
                ForecastWeather.date_time <= end_date,
            )
            .group_by(
                ForecastWeather.location_id,
                func.date_trunc("day", ForecastWeather.date_time),
            )
            .subquery()
        )

        # Calculate the average temperature difference for each location
        lowest_avg_temp_difference = (
            session.query(
                sub_query.c.location_id,
                func.avg(sub_query.c.temp_difference).label("average_difference"),
            )
            .group_by(sub_query.c.location_id)
            .order_by("average_difference")
            .first()
        )
        return {
            "city": session.query(Location)
            .filter(Location.id == lowest_avg_temp_difference[0])
            .first()
            .name,
            "average_daily_temperature_difference": round(
                lowest_avg_temp_difference[1], 2
            ),
        }


# Task 4


def get_day_with_highest_daily_temp_difference(city: str) -> dict:
    engine = get_db_engine()
    with Session(engine) as session:
        location = get_location(city, session)
        if not location:
            location = city
        location = fetch_data_if_not_present_in_db(session, 7, location)
        end_date = datetime.now() + timedelta(days=7)
        day_with_highest_temp_difference = (
            session.query(
                func.date_trunc("day", ForecastWeather.date_time),
                (
                    func.max(ForecastWeather.temp_c) - func.min(ForecastWeather.temp_c)
                ).label("temp_difference"),
                func.max(ForecastWeather.temp_c),
                func.min(ForecastWeather.temp_c),
            )
            .filter(
                ForecastWeather.date_time >= datetime.now(),
                ForecastWeather.date_time <= end_date,
                ForecastWeather.location == location,
            )
            .group_by(func.date_trunc("day", ForecastWeather.date_time))
            .order_by(desc("temp_difference"))
            .first()
        )

        return {
            "date_with_highest_temperature_difference": str(
                day_with_highest_temp_difference[0]
            ),
            "highest_temperate": day_with_highest_temp_difference[2],
            "lowest_temperature": day_with_highest_temp_difference[3],
        }
