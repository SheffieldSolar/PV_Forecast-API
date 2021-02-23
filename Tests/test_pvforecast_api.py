"""
Unit tests for the pvforecast library.
Author: JamieTalor
First Authored: 2021-02-02
"""

import os
import unittest
from datetime import datetime, date
import pytz

import pandas.api.types as ptypes
from pvforecast_api import PVForecast

class PVForecastTestCase(unittest.TestCase):
    """Tests for `pvforecast.py`."""

    def setUp(self):
        """
        Setup the instance of class.
        """
        self.load_credentials()
        self.api = PVForecast(self.user_id, self.api_key)
        self.expected_dtypes = {
            "pes_id": ptypes.is_integer_dtype,
            "gsp_id": ptypes.is_integer_dtype,
            "forecast_base_gmt": ptypes.is_datetime64_any_dtype,
            "datetime_gmt": ptypes.is_datetime64_any_dtype,
            "generation_mw": ptypes.is_float_dtype,
            "bias_error": ptypes.is_float_dtype,
            "capacity_mwp": ptypes.is_float_dtype,
            "installedcapacity_mwp": ptypes.is_float_dtype,
            "lcl_mw": ptypes.is_float_dtype,
            "stats_error": ptypes.is_float_dtype,
            "ucl_mw": ptypes.is_float_dtype,
            "uncertainty_MW": ptypes.is_float_dtype,
            "site_count": ptypes.is_integer_dtype
        }

    def load_credentials(self):
        creds_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "credentials.txt")
        with open(creds_file, "r") as fid:
            self.user_id, self.api_key = fid.readlines()[0].strip().split(":")

    def check_df_dtypes(self, api_df):
        """
        Check the dtypes of a Pandas DataFrame
        against the expected dtypes from the API.
        """
        for column in api_df.columns:
            with self.subTest(column=column):
                assert self.expected_dtypes[column](api_df[column])

    def check_gsp_list_dtypes(self, data):
        """
        Check the dtypes of a gsp tuple
        against the expected dtypes from the API.
        """
        with self.subTest(column="gsp_id"):
            assert all([isinstance(d[0], int) for d in data])
        self.check_list_dtypes(data)

    def check_pes_list_dtypes(self, data):
        with self.subTest(column="pes_id"):
            assert all([isinstance(d[0], int) for d in data])
        self.check_list_dtypes(data)

    def check_list_dtypes(self, data):
        """
        Check the dtypes of a list of lists against the expected dtypes from the API.
        """
        with self.subTest(column="forecast_base_gmt"):
            assert all([isinstance(d[1], str) for d in data])
        with self.subTest(column="datetime_gmt"):
            assert all([isinstance(d[2], str) for d in data])
        with self.subTest(column="generation_mw"):
            assert all([isinstance(d[3], float) for d in data])

    def check_list(self, data):
        """
        Check the length of the returned list of lists against the expected length.
        """
        with self.subTest():
            assert isinstance(data, list) and len(data[0]) == 4

    def check_df_columns(self, data):
        """
        Check the columns of the returned DataFrame
        against the expected columns.
        """
        with self.subTest():
            assert (("pes_id" in data or "gsp_id" in data) and "forecast_base_gmt" in data
                    and "datetime_gmt" in data and "generation_mw" in data)

    def test_latest(self):
        """Tests the latest function."""
        data = self.api.latest(entity_type="pes", entity_id=0)
        self.check_list(data)
        self.check_pes_list_dtypes(data)
        data = self.api.latest(entity_type="pes", entity_id=0, dataframe=True)
        self.check_df_columns(data)
        self.check_df_dtypes(data)
        data = self.api.latest(entity_type="pes", entity_id=0,
                               extra_fields="installedcapacity_mwp",
                               dataframe=True)
        self.check_df_columns(data)
        self.check_df_dtypes(data)
        data = self.api.latest(entity_type="gsp", entity_id=103)
        self.check_list(data)
        self.check_gsp_list_dtypes(data)
        data = self.api.latest(entity_type="gsp", entity_id=103, dataframe=True)
        self.check_df_columns(data)
        self.check_df_dtypes(data)

    def test_get_forecasts(self):
        """Test the get_forecasts function."""
        # Temporarily deprecated
        return

    def test_get_forecast(self):
        """Test the get_forecast function."""
        data = self.api.get_forecast(forecast_base_gmt=datetime(2021, 2, 2, 7, 0, tzinfo=pytz.utc),
                                     entity_type="pes", entity_id=0)
        self.check_list(data)
        self.check_pes_list_dtypes(data)
        data = self.api.get_forecast(forecast_base_gmt=datetime(2021, 2, 2, 7, 0, tzinfo=pytz.utc),
                                     entity_type="pes", entity_id=0, dataframe=True)
        self.check_df_columns(data)
        self.check_df_dtypes(data)
        data = self.api.get_forecast(forecast_base_gmt=datetime(2021, 2, 2, 7, 0, tzinfo=pytz.utc),
                                     entity_type="pes", entity_id=0,
                                     extra_fields="installedcapacity_mwp", dataframe=True)
        self.check_df_dtypes(data)
        data = self.api.get_forecast(forecast_base_gmt=datetime(2021, 2, 2, 7, 0, tzinfo=pytz.utc),
                                     entity_type="gsp", entity_id=26)
        self.check_list(data)
        self.check_gsp_list_dtypes(data)
        data = self.api.get_forecast(forecast_base_gmt=datetime(2021, 2, 2, 7, 0, tzinfo=pytz.utc),
                                     entity_type="gsp", entity_id=26, dataframe=True)
        self.check_df_columns(data)
        self.check_df_dtypes(data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
