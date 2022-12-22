"""
A Python interface for the PV_Forecast web API from Sheffield Solar.

- Jamie Taylor <jamie.taylor@sheffield.ac.uk>
- Ethan Jones <ejones18@sheffield.ac.uk>
- First Authored: 2018-08-31
- Updated: 2022-12-10 to provide support for proxy connections & CLI.
"""

import os
import sys
from datetime import datetime, timedelta, date, time
from math import ceil
from time import sleep
from typing import List, Union, Tuple
import json
import pytz
import requests
import argparse

from numpy import nan, int64
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

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
    `user_id` : string
        A valid User ID for the PV_Forecast API.
    `api_key` : string
        A valid API Key for the PV_Forecast API (must correspond to the given *user_id*).
    `retries` : int
        Optionally specify the number of retries to use should the API respond with anything
        other than status code 200. Exponential back-off applies inbetween retries.
    `proxies` : Dict
        Optionally specify a Dict of proxies for http and https requests in the format:
        {"http": "<address>", "https": "<address>"}
    Notes
    -----
    To obtain a User ID and API key, please visit the `PV_Forecast API website <https://api.solar.sheffield.ac.uk/pvforecast/>`_.
    """
    def __init__(self, user_id, api_key, retries=3, proxies=None):
        self.proxies = proxies
        self.base_url = "https://api0.solar.sheffield.ac.uk/pvforecast/api/v4/"
        self.retries = retries
        self.params = {"user_id": user_id, "key": api_key, "data_format": "json"}
        self.gsp_list = self._get_gsp_list()
        self.pes_list = self._get_pes_list()
        self.gsp_ids = self.gsp_list.gsp_id.dropna().astype(int64).unique()
        self.pes_ids = self.pes_list.pes_id.dropna().astype(int64).unique()

    def _get_gsp_list(self):
        """Fetch the GSP list from the API and convert to Pandas DataFrame."""
        url = f"{self.base_url}/gsp_list"
        response = self._fetch_url(url)
        return pd.DataFrame(response["data"], columns=response["meta"])

    def _get_pes_list(self):
        """Fetch the PES list from the API and convert to Pandas DataFrame."""
        url = f"{self.base_url}/pes_list"
        response = self._fetch_url(url)
        return pd.DataFrame(response["data"], columns=response["meta"])

    def latest(self, 
               entity_type: str = "gsp",
               entity_id: int = 0,
               extra_fields: str = "",
               dataframe: bool = False) -> Union[List, pd.DataFrame]:
        """
        Get the latest PV_Forecast from the API.

        Parameters
        ----------
        `entity_type` : string
            The aggregation entity type of interest, either "pes" or "gsp". Defaults to "gsp".
        `entity_id` : int
            The numerical ID of the entity of interest. Defaults to 0 (national).
        `extra_fields` : string
            Comma-separated string listing any extra fields.
        `dataframe` : boolean
            Set to True to return data as a Pandas DataFrame. Default is False, i.e. return a list.

        Returns
        -------
        list
            Each element of the outter list is a list containing the pes_id or gsp_id,
            forecast_base_gmt, datetime_gmt and generation_mw fields of a PV_Forecast, plus any
            extra_fields in the order specified.
        OR
        Pandas DataFrame
            Contains the columns pes_id or gsp_id, forecast_base_gmt, datetime_gmt and
            generation_mw, plus any extra_fields in the order specified.

        Notes
        -----
        For list of optional *extra_fields*, see `PV_Forecast API Docs
        <https://api.solar.sheffield.ac.uk/pvforecast/docs>`_.
        """
        return self.get_forecast(entity_type=entity_type, entity_id=entity_id,
                                 extra_fields=extra_fields, dataframe=dataframe)

    def get_forecast(self,
                     forecast_base_gmt: datetime = None,
                     entity_type: str = "gsp",
                     entity_id: int = 0,
                     extra_fields: str = "",
                     dataframe: bool = False) -> Union[List, pd.DataFrame]:
        """
        Get the PV_Forecast with a given forecast base from the API.

        Parameters
        ----------
        `forecast_base_gmt` : datetime
            A timezone-aware datetime object.
        `entity_type` : string
            The aggregation entity type of interest, either "pes" or "gsp". Defaults to "gsp".
        `entity_id` : int
            The numerical ID of the entity of interest. Defaults to 0 (national).
        `extra_fields` : string
            Comma-separated string listing any extra fields.
        `dataframe` : boolean
            Set to True to return data as a Pandas DataFrame. Default is False, i.e. return a list.

        Returns
        -------
        list
            Each element of the outter list is a list containing the pes_id or gsp_id,
            forecast_base_gmt, datetime_gmt and generation_mw fields of a PV_Forecast, plus any
            extra_fields in the order specified.
        OR
        Pandas DataFrame
            Contains the columns pes_id or gsp_id, forecast_base_gmt, datetime_gmt and
            generation_mw, plus any extra_fields in the order specified.

        Notes
        -----
        For list of optional *extra_fields*, see `PV_Forecast API Docs
        <https://api.solar.sheffield.ac.uk/pvforecast/docs>`_.
        """
        return self._get_forecast(forecast_base_gmt, entity_type, entity_id, extra_fields,
                                  dataframe)[0]

    def _get_forecast(self, forecast_base_gmt=None, entity_type="pes", entity_id=0, extra_fields="",
                      dataframe=False):
        """
        Get the PV_Forecast with a given forecast base from the API, returning both the data and the
        column names.
        """
        self._validate_inputs(forecast_base_gmt=forecast_base_gmt, entity_type=entity_type,
                              entity_id=entity_id, extra_fields=extra_fields)
        params = self._compile_params(forecast_base_gmt, extra_fields)
        response = self._query_api(entity_type, entity_id, params)
        if dataframe:
            return self._convert_tuple_to_df(response["data"], response["meta"]), response["meta"]
        return response["data"], response["meta"]

    def get_forecast_bases(self,
                           start: datetime,
                           end: datetime,
                           forecast_type: str = "national") -> List[str]:
        """
        Get a list of the forecast base times available on the API between two datetimes.

        Parameters
        ----------
        `start` : datetime
            A timezone-aware datetime object.
        `end` : datetime
            A timezone-aware datetime object.
        `forecast_type` : str
            Either 'national' or 'regional'.

        Returns
        -------
        list
            A list of valid forecast base times as strings.
        """
        self._validate_start_end(start, end)
        if forecast_type.lower() == "national":
            gsp_id = 0
        elif forecast_type.lower() == "regional":
            gsp_id = 1
        else:
            raise PVForecastException("forecast_type must be 'national' or 'regional'.")
        params = {"start": self._iso8601_ss(start), "end": self._iso8601_ss(end)}
        response = self._query_api("forecast_bases_list", gsp_id, params)
        return response

    def get_forecasts(self,
                      start: datetime,
                      end: datetime,
                      forecast_base_times: List[str] = [],
                      entity_type: str = "gsp",
                      entity_id: int = 0,
                      extra_fields: str = "",
                      dataframe: bool = False) -> Union[List, pd.DataFrame]:
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
            The default behaviour (an empty list) is to download all forecast base times.
        `entity_type` : string
            The aggregation entity type of interest, either "pes" or "gsp". Defaults to "gsp".
        `entity_id` : int
            The numerical ID of the entity of interest. Defaults to 0 (national).
        `extra_fields` : string
            Comma-separated string listing any extra fields.
        `dataframe` : boolean
            Set to True to return data as a Pandas DataFrame. Default is False, i.e. return a list.

        Returns
        -------
        list
            Each element of the outter list is a list containing the pes_id or gsp_id,
            forecast_base_gmt, datetime_gmt and generation_mw fields of a PV_Forecast, plus any
            extra_fields in the order specified.
        OR
        Pandas DataFrame
            Contains the columns pes_id or gsp_id, forecast_base_gmt, datetime_gmt and
            generation_mw, plus any extra_fields in the order specified.

        Notes
        -----
        For list of optional *extra_fields*, see `PV_Forecast API Docs
        <https://api.solar.sheffield.ac.uk/pvforecast/docs>`_.
        """
        self._validate_start_end(start, end)
        self._validate_inputs(entity_type=entity_type, entity_id=entity_id,
                              extra_fields=extra_fields)
        try:
            dummy = [datetime.strptime(t, "%H:%M") for t in forecast_base_times]
        except ValueError:
            raise PVForecastException("forecast_base_times must be a list of time strings in the "
                                      "format HH:MM.")
        forecast_type = "national" if entity_id == 0 else "regional"
        fbases = self.get_forecast_bases(start, end, forecast_type)
        fbases = [datetime.fromisoformat(fb.replace("Z", "+00:00")) for fb in fbases]
        data = []
        meta = []
        for fbase in fbases:
            if not forecast_base_times or fbase.strftime("%H:%M") in forecast_base_times:
                data_, meta_= self._get_forecast(forecast_base_gmt=fbase, entity_type=entity_type,
                                                entity_id=entity_id, extra_fields=extra_fields)
                if data_:
                    data += data_
                    meta = meta_
        if dataframe:
            return self._convert_tuple_to_df(data, meta)
        return data

    def _compile_params(self, forecast_base_gmt, extra_fields):
        """Compile parameters into a Python dict, formatting where necessary."""
        params = {}
        if forecast_base_gmt is not None:
            params["forecast_base_GMT"] = self._iso8601_ss(forecast_base_gmt)
        if extra_fields:
            params["extra_fields"] = extra_fields
        params.update(self.params)
        return params

    def _iso8601_ss(self, dt):
        return dt.isoformat().replace("+00:00", "Z")

    def _query_api(self, entity_type, entity_id, params):
        """Query the API with some REST parameters."""
        url = self._build_url(entity_type, entity_id, params)
        return self._fetch_url(url)

    def _build_url(self, entity_type, entity_id, params):
        """Construct the appropriate URL for a given set of parameters."""
        base_url = "{}{}/{}".format(self.base_url, entity_type, entity_id)
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
                page = requests.get(url, proxies=self.proxies)
                page.raise_for_status()
                if page.status_code == 200 and "Your api key is not valid" in page.text:
                    raise PVForecastException("The user_id and/or api_key entered are invalid.")
                if page.status_code == 200 and "Your account does not give access" in page.text:
                    raise PVForecastException("The user_id and api_key does not give access to the "
                                              "data you've requested, contact Sheffield Solar "
                                              "<pvforecast@sheffield.ac.uk>.")
                success = True
            except requests.exceptions.HTTPError:
                sleep(delay)
                delay *= 2
                continue
        if not success:
            raise PVForecastException("Error communicating with the PV_Forecast API.")
        try:
            return json.loads(page.text)
        except:
            raise PVForecastException("Error communicating with the PV_Forecast API.")

    def _validate_start_end(self, start, end):
        type_check = not (isinstance(start, datetime) and isinstance(end, datetime))
        tz_check = start.tzinfo is None or end.tzinfo is None
        if type_check or tz_check:
            raise PVForecastException("start and end must be timezone-aware Python datetime "
                                      "objects.")
        if end < start:
            raise PVForecastException("end must be later than start.")

    def _validate_inputs(self, forecast_base_gmt=None, entity_type="pes", entity_id=0,
                         extra_fields=""):
        """Validate common input parameters."""
        if forecast_base_gmt is not None:
            if not isinstance(forecast_base_gmt, datetime) or forecast_base_gmt.tzinfo is None:
                raise PVForecastException("The forecast_base_gmt must be a timezone-aware Python "
                                          "datetime object.")
        if not isinstance(entity_type, str):
            raise PVForecastException("The entity_type must be a string.")
        if entity_type not in ["pes", "gsp"]:
            raise PVForecastException("The entity_type must be either 'pes' or 'gsp'.")
        if not isinstance(extra_fields, str):
            raise PVForecastException("The extra_fields must be a comma-separated string (with no "
                                      "spaces).")
        if entity_type == "pes":
            if entity_id != 0 and entity_id not in self.pes_ids:
                raise PVForecastException(f"The pes_id {entity_id} was not found.")
        elif entity_type == "gsp":
            if entity_id not in self.gsp_ids:
                raise PVForecastException(f"The gsp_id {entity_id} was not found.")

    def _convert_tuple_to_df(self, data, columns):
        """Converts a tuple of values to a data-frame object."""
        data = [data] if isinstance(data, tuple) else data
        data = [tuple(nan if d is None else d for d in t) for t in data]
        data = pd.DataFrame(data, columns=list(map(str.lower, columns)))
        if "forecast_base_gmt" in data.columns:
            data.forecast_base_gmt = pd.to_datetime(data.forecast_base_gmt)
        if "datetime_gmt" in data.columns:
            data.datetime_gmt = pd.to_datetime(data.datetime_gmt)
        return data

def parse_options():
    """Parse command line options."""
    parser = argparse.ArgumentParser(description=("This is a command line interface (CLI) for the "
                                                  "PVForecast API module"),
                                     epilog="Jamie Taylor & Ethan Jones, 2022-12-10")
    parser.add_argument("--user_id", metavar="<user_id>", dest="user_id", action="store",
                        type=str, required=True, help="PVForecast user id.")
    parser.add_argument("--api_key", metavar="<api_key>", dest="api_key", action="store",
                        type=str, required=False, help="Your PVForecast API key. "
                        "If not path passed, will check environment variables for `PVForecastAPIKey` "
                        "and finally a config file in same directory named `.pvforecast_credentials` ")
    parser.add_argument("-s", "--start", metavar="\"<yyyy-mm-dd HH:MM:SS>\"", dest="start",
                        action="store", type=str, required=False, default=None,
                        help="Specify a UTC start date in 'yyyy-mm-dd HH:MM:SS' format "
                             "(inclusive), default behaviour is to retrieve the latest outturn.")
    parser.add_argument("-e", "--end", metavar="\"<yyyy-mm-dd HH:MM:SS>\"", dest="end",
                        action="store", type=str, required=False, default=None,
                        help="Specify a UTC end date in 'yyyy-mm-dd HH:MM:SS' format (inclusive), "
                        "default behaviour is to retrieve the latest outturn.")
    parser.add_argument("--entity_type", metavar="<entity_type>", dest="entity_type",
                        action="store", type=str, required=False, default="gsp",
                        choices=["gsp", "pes"],
                        help="Specify an entity type, either 'gsp' or 'pes'. Default is 'gsp'.")
    parser.add_argument("--entity_id", metavar="<entity_id>", dest="entity_id", action="store",
                        type=int, required=False, default=0,
                        help="Specify an entity ID, default is 0 (i.e. national).")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                        required=False, help="Specify to not print anything to stdout.")
    parser.add_argument("-o", "--outfile", metavar="</path/to/output/file>", dest="outfile",
                        action="store", type=str, required=False,
                        help="Specify a CSV file to write results to.")
    parser.add_argument('-http', '-http-proxy', metavar="<http_proxy>", dest="http",
                        type=str, required=False, default=None, action="store",
                        help="HTTP Proxy address")
    parser.add_argument('-https', '-https-proxy', metavar="<https_proxy>", dest="https",
                        type=str, required=False, default=None, action="store",
                        help="HTTPS Proxy address")
    options = parser.parse_args()

    def handle_options(options):
        """Validate command line args and pre-process where necessary."""
        if options.api_key is None:
            key = os.environ.get('PVForecastAPIKey')
            if key is None:
                config_path = os.path.join(SCRIPT_DIR, ".pvforecast_credentials")
                if os.path.exists(config_path):
                    with open(config_path) as f:
                        key = f.read()
            if key is None:
                raise Exception("OptionsError: Couldn't fetch API Key, ensure either the file path is "
                                "passed via the CLI, the `PVForecastAPIKey` environment variable is "
                                "defined or it exists in the `C:\PVForecastAPIKey.yaml` config file.")
            else:
                options.api_key = key
        if (options.outfile is not None and os.path.exists(options.outfile)) and not options.quiet:
            try:
                input(f"The output file '{options.outfile}' already exists and will be "
                      "overwritten, are you sure you want to continue? Press enter to continue or "
                      "ctrl+c to abort.")
            except KeyboardInterrupt:
                print()
                print("Aborting...")
                sys.exit(0)
        if options.start is not None:
            try:
                options.start = pytz.utc.localize(
                    datetime.strptime(options.start, "%Y-%m-%d %H:%M:%S")
                )
            except:
                raise Exception("OptionsError: Failed to parse start datetime, make sure you use "
                                "'yyyy-mm-dd HH:MM:SS' format.")
        if options.end is not None:
            try:
                options.end = pytz.utc.localize(datetime.strptime(options.end, "%Y-%m-%d %H:%M:%S"))
            except:
                raise Exception("OptionsError: Failed to parse end datetime, make sure you use "
                                "'yyyy-mm-dd HH:MM:SS' format.")
        proxies = {}
        if options.http is not None:
            proxies.update({"http": options.http})
        if options.https is not None:
            proxies.update({"https": options.https})
        options.proxies = proxies
        return options
    return handle_options(options)

def main():
    options = parse_options()
    pvforecast = PVForecast(options.user_id, options.api_key, proxies=options.proxies)
    if options.start is None and options.end is None:
        data = pvforecast.latest(entity_type=options.entity_type, entity_id=options.entity_id,
                                 dataframe=True)
    else:
        start = datetime(2014, 1, 1, 0, 30, tzinfo=pytz.utc) if options.start is None \
            else options.start
        end = pytz.utc.localize(datetime.utcnow()) if options.end is None else options.end
        data = pvforecast.get_forecasts(start, end, entity_type=options.entity_type,
                                        entity_id=options.entity_id, dataframe=True)
    if options.outfile is not None:
        data.to_csv(options.outfile, float_format="%.3f", index=False)
    if not options.quiet:
        print(data)
if __name__ == "__main__":
    main()
