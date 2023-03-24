from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy_serializer import SerializerMixin


class Base(DeclarativeBase):
    pass


class Weather:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @declared_attr
    def location(self) -> Mapped["Location"]:
        return relationship("Location")

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=False)
    date_time: Mapped[datetime] = mapped_column(nullable=False)
    temp_c: Mapped[float]
    condition: Mapped[str]
    visibility_km: Mapped[float]
    humidity_percent: Mapped[float]
    realfeel_c: Mapped[float]
    wind_speed_mph: Mapped[float]
    wind_pressure_in: Mapped[float]
    cloud_cover_percent: Mapped[float]
    air_quality: Mapped[str] = mapped_column(nullable=True)
    __table_args__ = (UniqueConstraint("location_id", "date_time"),)


class CurrentWeather(Base, Weather, SerializerMixin):
    __tablename__ = "current_weather"


class ForecastWeather(Base, Weather, SerializerMixin):
    __tablename__ = "forecast_weather"

    wind_gust_mph: Mapped[float]
    dew_point_c: Mapped[float]
    probability_of_rain_percent: Mapped[float]
    probability_of_snow_percent: Mapped[float]


class Location(Base, SerializerMixin):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    region: Mapped[str]
    country: Mapped[str] = mapped_column(nullable=False)
    lat: Mapped[float]
    lon: Mapped[float]
    tz_id: Mapped[str]
    __table_args__ = (UniqueConstraint("lat", "lon"),)
