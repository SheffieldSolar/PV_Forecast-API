"""
A Python interface for the PV_Forecast web API from Sheffield Solar.

- Jamie Taylor <jamie.taylor@sheffield.ac.uk>
- First Authored: 2018-08-31
"""

from __future__ import print_function
from datetime import datetime, timedelta, date, time
from math import ceil
from time import sleep
import pytz
import requests

class PVForecastException(Exception):
    """An Exception specific to the PVForecast class."""
    def __init__(self, msg):
        try:
            caller_file = inspect.stack()[2][1]
        except:
            import os
            caller_file = os.path.basename(__file__)
        self.msg = "%s (in '%s')" % (msg, caller_file)
    def __str__(self):
        return self.msg

class PVForecast:
    """
    Interface with the PV_Forecast web API.
    
    Parameters
    ----------
    `retries` : int
        Optionally specify the number of retries to use should the API respond with anything
        other than status code 200. Exponential back-off applies inbetween retries.
    """
    def __init__(self, user_id, api_key, retries=3):
        if not user_id or not api_key:
            raise PVForecastException("You must pass a valid user_id and api_key.")
        self.base_url = "https://api.solar.sheffield.ac.uk/pvforecast/v0"
        self.retries = retries
        self.params = {"user_id": user_id, "key": api_key}

    def latest(self, region_id=0):
        """
        Get the latest PV_Forecast from the API.

        Parameters
        ----------
        `region_id` : int
            The numerical ID of the region of interest. Defaults to 0 (i.e. national).
        Returns
        -------
        list
            Each element of the outter list is a list containing the region_id, forecast_base_GMT,
            datetime_GMT, generation_MW, capacity_MWp and installed_capacity_MWp fields of a
            PV_Forecast.
        """
        return self.get_forecast(region_id=region_id)

    def get_forecast(self, forecast_base_gmt=None, region_id=0):
        """
        Get the PV_Forecast with a given forecast base from the API.

        Parameters
        ----------
        `forecast_base_gmt` : datetime
            A timezone-aware datetime object. Will be corrected to the END of the half hour in which
            *dt* falls, since Sheffield Solar use end of interval as convention.
        `region_id` : int
            The numerical ID of the region of interest. Defaults to 0 (i.e. national).
        Returns
        -------
        Returns
        -------
        list
            Each element of the outter list is a list containing the region_id, forecast_base_GMT,
            datetime_GMT, generation_MW, capacity_MWp and installed_capacity_MWp fields of a
            PV_Forecast.
        """
        if not isinstance(forecast_base_gmt, datetime) or forecast_base_gmt.tzinfo is None:
            PVForecastException("The forecast_base_gmt must be a timezone-aware Python datetime "
                            "object.")
        params = self._compile_params(region_id, forecast_base_gmt)
        response = self._query_api(params)
        return self._parse_response(response)

    def get_forecasts(self, start, end, forecast_base_times=[], region_id=0):
        """
        Get multiple PV_Forecasts during a given time interval from the API.

        Parameters
        ----------
        `start` : datetime
            A timezone-aware datetime object.
        `end` : datetime
            A timezone-aware datetime object.
        `forecast_base_times` : list
            Optionally provide a list of forecast base times of interest (e.g. ["07:00", "10:00"]).
            The default behaviour (an empty list) is to download all forecast bas times.
        `region_id` : int
            The numerical ID of the region of interest. Defaults to 0 (i.e. national).
        Returns
        -------
        list
            Each element of the outter list is a list containing the region_id, forecast_base_GMT,
            datetime_GMT, generation_MW, capacity_MWp and installed_capacity_MWp fields of a
            PV_Forecast.
        """
        type_check = not (isinstance(start, datetime) and isinstance(end, datetime))
        tz_check = start.tzinfo is None or end.tzinfo is None
        if type_check or tz_check:
            PVForecastException("Start and end must be timezone-aware Python datetime objects.")
        data = []
        forecast_base = self._nearest_fbase(start)
        while forecast_base <= end:
            if not forecast_base_times or forecast_base.strftime("%H:%M") in forecast_base_times:
                data += self.get_forecast(forecast_base_gmt=forecast_base, region_id=0)
            forecast_base += timedelta(hours=3)
        return data

    def _parse_response(self, response):
        """Parse the CSV data returned by the API."""
        data = []
        parse_dt = lambda ds: pytz.utc.localize(datetime.strptime(ds, "%Y-%m-%d %H:%M:%S"))
        for line in response.split("\r\n")[1:]:
            if not line:
                continue
            row = line.strip().split(",")
            data.append([int(row[0]), parse_dt(row[1]), parse_dt(row[2]), float(row[3]),
                         float(row[4]), float(row[5])])
        return data

    def _compile_params(self, region_id=0, forecast_base_gmt=None):
        """Compile parameters into a Python dict, formatting where necessary."""
        self.params.update({"substation_id": region_id})
        if forecast_base_gmt is not None:
            self.params.update({"forecast_base_GMT": forecast_base_gmt.isoformat()})
        return self.params

    def _query_api(self, params):
        """Query the API with some REST parameters."""
        url = self._build_url(params)
        # print(url)
        return self._fetch_url(url)

    def _build_url(self, params):
        """Construct the appropriate URL for a given set of parameters."""
        base_url = self.base_url
        url = base_url + "?" + "&".join(["{}={}".format(k, params[k]) for k in params])
        return url

    def _fetch_url(self, url):
        """Fetch the URL with GET request."""
        success = False
        try_counter = 0
        delay = 0.5
        while not success and try_counter < self.retries + 1:
            try_counter += 1
            try:
                page = requests.get(url)
                page.raise_for_status()
                if page.status_code == 200 and "no matching, current token found" in page.text:
                    raise PVForecastException("The user_id and/or api_key entered are invalid.")
                success = True
            except requests.exceptions.HTTPError:
                sleep(delay)
                delay *= 2
                continue
            except:
                raise
        if not success:
            raise PVForecastException("Error communicating with the PV_Forecast API.")
        try:
            return page.text
        except:
            raise PVForecastException("Error communicating with the PV_Forecast API.")

    def _nearest_fbase(self, dt):
        """Round a given datetime object up to the nearest forecast base time."""
        target_hour = ceil((dt.hour - 1) / 3.) * 3 + 1
        dt -= timedelta(minutes=dt.minute, seconds=dt.second)
        dt += timedelta(hours=target_hour - dt.hour)
        return dt

def main():
    """Demo the module's capabilities."""
    print("Demo the PV_Forecast module's capabilities...")
    import time as TIME
    timerstart = TIME.time() #Time the script to monitor performance
    pvforecast = PVForecast(user_id="", api_key="")  # Add your user_id and api_key!
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
