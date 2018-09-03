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
    timerstart = TIME.time() #Time the script to monitor performance
    pvforecast = PVForecast(user_id="", api_key="") # Add your user_id and api_key!
    print("Latest: ")
    print(pvforecast.latest())
    print("Time taken: {} seconds".format(TIME.time() - timerstart))
    print("Forecast Base 2018-08-31 07:00: ")
    print(pvforecast.get_forecast(datetime(2018, 8, 31, 7, 0, tzinfo=pytz.utc)))
    print("Time taken: {} seconds".format(TIME.time() - timerstart))
    # print("Between 2018-08-01 00:00 and 2018-08-07 23:00: ")
    # print(pvforecast.get_forecasts(datetime(2018, 8, 1, 0, 0, tzinfo=pytz.utc),
                                   # datetime(2018, 8, 7, 23, 0, tzinfo=pytz.utc)))
    # print("Time taken: {} seconds".format(TIME.time() - timerstart))
    print("Between 2018-08-01 00:00 and 2018-08-07 23:00, only 07:00 forecast: ")
    print(pvforecast.get_forecasts(datetime(2018, 8, 1, 0, 0, tzinfo=pytz.utc),
                                   datetime(2018, 8, 7, 23, 0, tzinfo=pytz.utc),
                                   forecast_base_times=["07:00"]))
    print("Time taken: {} seconds".format(TIME.time() - timerstart))

if __name__ == "__main__":
    main()
