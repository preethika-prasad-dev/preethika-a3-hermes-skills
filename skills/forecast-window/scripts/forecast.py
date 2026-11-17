"""Fetch two local calendar days of weather, with a U.S. fallback."""

import argparse
from datetime import date
import json
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


API = "https://api.open-meteo.com/v1/forecast"
FIELDS = ("temperature_2m_min", "temperature_2m_max", "precipitation_probability_max")


def normalize(payload: dict) -> dict:
    """Extract the documented result fields and validate parallel arrays."""
    daily = payload["daily"]
    dates = daily["time"]
    if not dates or any(len(daily[field]) != len(dates) for field in FIELDS):
        raise ValueError("Forecast days and values do not match.")
    days = [
        {
            "date": date.fromisoformat(day).isoformat(),
            "low_f": daily["temperature_2m_min"][index],
            "high_f": daily["temperature_2m_max"][index],
            "precipitation_probability_percent": daily["precipitation_probability_max"][index],
        }
        for index, day in enumerate(dates)
    ]
    return {"timezone": payload["timezone"], "days": days, "source": "https://open-meteo.com/"}


def forecast(latitude: float, longitude: float) -> dict:
    # Adapted from https://open-meteo.com/en/docs
    # - request only the daily temperature and precipitation fields used by this skill.
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Latitude or longitude is outside the supported range.")
    params = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join(FIELDS),
        "forecast_days": 2,
        "temperature_unit": "fahrenheit",
        "timezone": "auto",
    })
    try:
        with urlopen(f"{API}?{params}", timeout=5) as response:
            return normalize(json.load(response))
    except (OSError, URLError):
        return forecast_nws(latitude, longitude)


def forecast_nws(latitude: float, longitude: float) -> dict:
    # Adapted from https://www.weather.gov/documentation/services-web-api
    # - resolve a point to a validated grid forecast and normalize its periods.
    headers = {"User-Agent": "Forecast Window CSCI599 course project",
               "Accept": "application/geo+json"}
    point = Request(f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}", headers=headers)
    with urlopen(point, timeout=7) as response:
        metadata = json.load(response)["properties"]
    endpoint = urlsplit(metadata["forecast"])
    if endpoint.scheme != "https" or endpoint.netloc != "api.weather.gov" or not endpoint.path.startswith("/gridpoints/"):
        raise ValueError("Unexpected National Weather Service forecast location.")
    with urlopen(Request(endpoint.geturl(), headers=headers), timeout=7) as response:
        periods = json.load(response)["properties"]["periods"]
    days = {}
    for period in periods:
        day = date.fromisoformat(period["startTime"][:10]).isoformat()
        row = days.setdefault(day, {"date": day, "high_f": None, "low_f": None,
                                    "precipitation_probability_percent": None})
        if period.get("temperatureUnit") == "F":
            row["high_f" if period["isDaytime"] else "low_f"] = period["temperature"]
        probability = (period.get("probabilityOfPrecipitation") or {}).get("value")
        if isinstance(probability, (int, float)):
            row["precipitation_probability_percent"] = max(
                probability, row["precipitation_probability_percent"] or 0,
            )
    if not days:
        raise ValueError("The National Weather Service returned no forecast periods.")
    return {"timezone": metadata["timeZone"], "days": list(days.values())[:2],
            "source": endpoint.geturl()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("latitude", type=float)
    parser.add_argument("longitude", type=float)
    args = parser.parse_args()
    try:
        result = forecast(args.latitude, args.longitude)
    except (OSError, URLError, ValueError, KeyError, TypeError):
        parser.exit(1, "Forecast unavailable for those coordinates.\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
