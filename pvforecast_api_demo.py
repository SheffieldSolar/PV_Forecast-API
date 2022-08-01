"""
Demo script for the PVForecast-API library.
See https://github.com/SheffieldSolar/PV_Forecast-API for installation instructions.

- Jamie Taylor <jamie.taylor@sheffield.ac.uk>
- First Authored: 2018-08-31
"""

from datetime import datetime
import pytz
import time as TIME

from pvforecast_api import PVForecast

def main():
    """Demo the module's capabilities."""
    pvforecast = PVForecast(user_id="", api_key="") # Add your user_id and api_key!
    print("Latest national forecast:")
    print(pvforecast.latest())
    print("Latest national forecast as DataFrame:")
    print(pvforecast.latest(dataframe=True))
    print("Latest forecast for PES 23 as DataFrame:")
    print(pvforecast.latest(entity_id=23, dataframe=True))
    print("Latest forecast for GSP 120 as DataFrame:")
    print(pvforecast.latest(entity_type="gsp", entity_id=120, dataframe=True))
    print("National forecast with forecast base `2022-07-19 07:00` as DataFrame:")
    print(pvforecast.get_forecast(datetime(2022, 7, 19, 7, 0, tzinfo=pytz.utc), dataframe=True))
    print("National forecasts made between `2022-07-19 00:00` and `2022-07-19 23:00`, as "
          "DataFrame: ")
    print(pvforecast.get_forecasts(datetime(2022, 7, 19, 0, 0, tzinfo=pytz.utc),
                                   datetime(2022, 7, 19, 23, 0, tzinfo=pytz.utc), dataframe=True))
    print("National forecasts made between `2022-07-19 00:00` and `2022-07-21 23:00`, only "
          "including 07:00 forecast, as DataFrame: ")
    print(pvforecast.get_forecasts(datetime(2022, 7, 19, 0, 0, tzinfo=pytz.utc),
                                   datetime(2022, 7, 21, 23, 0, tzinfo=pytz.utc),
                                   forecast_base_times=["07:00"], dataframe=True))
    print("Forecasts for GSP 120 made between `2022-07-19 00:00` and `2022-07-21 23:00`: ")
    print(pvforecast.get_forecasts(datetime(2022, 7, 19, 0, 0, tzinfo=pytz.utc),
                                   datetime(2022, 7, 21, 23, 0, tzinfo=pytz.utc), entity_type="gsp",
                                   entity_id=120, dataframe=True))

if __name__ == "__main__":
    main()
