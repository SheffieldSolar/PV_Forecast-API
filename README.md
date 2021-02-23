
# PV_Forecast-API
A Python implementation of the PV_Forecast web API. See [www.solar.sheffield.ac.uk/pvforecast/](https://www.solar.sheffield.ac.uk/pvforecast/) and [api.solar.sheffield.ac.uk](https://api.solar.sheffield.ac.uk/)

**Latest Version: 0.2**

**New! Updated 2021-02-23 to use PV_Forecast API v3.**

## About this respository

* This Python library provides a convenient interface for the PV_Forecast web API to facilitate accessing PV_Forecast results in Python code.
* Developed and tested with Python 3.8, should work with Python 3.5+. Support for Python 2.7+ has been discontinued as of 2021-02-23.

## How do I get set up?

* Make sure you have Git installed - [Download Git](https://git-scm.com/downloads)
* Run `pip install git+https://github.com/SheffieldSolar/PV_Forecast-API`
* You will need a _User ID_ and _API Key_ for Sheffield Solar's PV_Forecast service - log in to the [PV_Forecast API website](https://api.solar.sheffield.ac.uk/pvforecast/) and go to the [User Area](https://api.solar.sheffield.ac.uk/pvforecast/user) to find yours.

## Usage

There are three methods for extracting raw data from the PV_Live API:

|Method|Description|Docs Link|
|------|-----------|---------|
|`PVForecast.latest(entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get the latest PV forecast from the API.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.latest)|
|`PVForecast.get_forecast(forecast_base_gmt=None, entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get the PV forecast for a given forecast base from the API.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.get_forecast)|
|`PVForecast.get_forecasts(start, end, forecast_base_times=[], entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get all PV forecasts during a given time interval from the API. This method is temporarily deprecated but will return in a future version of this code.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.get_forecasts)|

These methods include the following optional parameters:

|Parameter|Usage|
|---------|-----|
|`entity_type`|Choose between `"pes"` or `"gsp"`. If querying for national data, this parameter can be set to either value (or left to it's default value) since setting `entity_id` to `0` will always return national data.|
|`entity_id`|Set `entity_id=0` (the default value) to return nationally aggregated data. If `entity_type="pes"`, specify a _pes_id_ to retrieve data for, else if `entity_id="gsp"`, specify a _gsp_id_. For a full list of GSP and PES IDs, refer to the lookup table hosted on National Grid ESO's data portal [here](https://data.nationalgrideso.com/system/gis-boundaries-for-gb-grid-supply-points).|
|`extra_fields`|Use this to extract additional fields from the API such as _installedcapacity_mwp_. For a full list of available fields, see the [PV_Forecast API Docs](https://api.solar.sheffield.ac.uk/pvforecast/v3/docs).|
|`dataframe`|Set `dataframe=True` and the results will be returned as a Pandas DataFrame object which is generally much easier to work with. The columns of the DataFrame will be _pes_id_ or _gsp_id_, _forecast_base_gmt_, _datetime_gmt_, _generation_mw_, plus any extra fields specified.|

## Code Examples

See [pvforecast_api_demo.py](https://github.com/SheffieldSolar/PV_Forecast-API/blob/master/pvforecast_api_demo.py) for more example usage.

The examples below assume you have imported the PVForecast class and created a local instance called `pvf`:

```Python
from datetime import datetime
import pytz

from pvorecast_api import PVForecast

pvf = PVForecast(user_id="", api_key="") # Enter your user_id and api_key here!
```

|Example|Code|Example Output|
|-------|----|------|
|Get the latest nationally aggregated GB PV outturn forecast|`pvf.latest()`|`[[0, '2021-02-23T10:00:00Z', '2021-02-23T10:30:00Z', 2600.0], ..., [0, '2021-02-23T10:00:00Z', '2021-02-26T10:00:00Z', 5230.0]]`|
|Get the latest aggregated outturn forecast for **PES** region **23** (Yorkshire) as a DataFrame|`pvf.latest(entity_id=23, dataframe=True)`|![Screenshot of output](/misc/code_example_output1.png?raw=true)
|Get the latest aggregated outturn forecast for **GSP** ID **120** (INDQ1 or "Indian Queens")|`pvf.latest(entity_type="gsp", entity_id=120, dataframe=True)`|![Screenshot of output](/misc/code_example_output2.png?raw=true)
|Get the nationally aggregated GB PV outturn forecast with forecast base `2021-02-23T07:00:00Z` as a DataFrame|`pvf.get_forecast(datetime(2021, 2, 23, 7, 0, tzinfo=pytz.utc), dataframe=True))`|![Screenshot of output](/misc/code_example_output3.png?raw=true)|

## Documentation

* [https://sheffieldsolar.github.io/PV_Forecast-API/](https://sheffieldsolar.github.io/PV_Forecast-API/)

## How do I upgrade?

Sheffield Solar will endeavour to update this library in sync with the [PV_Forecast API](https://api.solar.sheffield.ac.uk/pvforecast/ "PV_Forecast API webpage"), but cannot guarantee this. If you have signed up for an account on the PV_Forecast API platform then you will be notified by email in advance of any changes to the API.

To upgrade the code:
* Run `pip install --upgrade git+https://github.com/SheffieldSolar/PV_Forecast-API`

## Who do I talk to?

* **Jamie Taylor** - [jamie.taylor@sheffield.ac.uk](mailto:jamie.taylor@sheffield.ac.uk "Email Jamie") - [SheffieldSolar](https://github.com/SheffieldSolar)

## Authors

* **Jamie Taylor** - [SheffieldSolar](https://github.com/SheffieldSolar)

## License

No license is defined yet - use at your own risk.
