
# PV_Forecast-API
A Python implementation of the PV_Forecast web API. See [www.solar.sheffield.ac.uk/pvforecast/](https://www.solar.sheffield.ac.uk/pvforecast/) and [api.solar.sheffield.ac.uk](https://api.solar.sheffield.ac.uk/)

**Latest Version: 0.5*

**New! Updated 2022-08-01 to use PV_Forecast API v4.**
**New! Updated 2022-12-12 to add support for proxy connections and add command line arguments.**

## About this repository

* This Python library provides a convenient interface for the PV_Forecast web API to facilitate accessing PV_Forecast results in Python code.
* Developed and tested with Python 3.10, should work with Python 3.7+. Support for Python 2.7+ has been discontinued as of 2021-02-23.

## About the PV_Forecast service

Sheffield Solar's PV_Forecast is a commercial service providing forecasts of half-hourly aggregated solar PV outturns across GB. You can sign up for a free trial via [api.solar.sheffield.ac.uk/pvforecast/](https://api.solar.sheffield.ac.uk/pvforecast/), but for continued access you'll need a paid subscription, for which you can email pvforecast@sheffield.ac.uk.

There are currently three tiers of Sheffield Solar's PV_Forecast service: Nationally-aggregated, Regionally-aggregated by DNO License Area (a.k.a PES or GSP Group) and Regionally-aggregated by Grid Supply Point (GSP).

The national forecast includes several updates per day whereas the regional forecasts are currently only updated once a day:

- The nationally aggregated PV forecast gives half hourly outturn estimates with regular updates:
    - 01:00, 02:00, 03:00, 04:00, 05:00, 06:00, 10:00, 13:00, 16:00, 19:00, 22:00 each day
        - Out to 72 hours
    - 07:00 each day
        - Out to 120 hours
- The regional forecast produces a half-hourly outturn estimate by GSP or by PES (a.k.a DNO License Area or GSP Group Region) with a single daily update (though we are looking to potentially add a second daily update):
    - 07:00 each day
        - Out to 72 hours

(N.B. Times above refer to the NWP releases from our weather forecast provider, DTN, the corresponding PV forecasts are available ~1 hour later once SS have trained and run the PV_Forecast model)

All of the operational and historical forecasts are accessible via a [fully documented web API](https://api.solar.sheffield.ac.uk/pvforecast/), for which this repository provides a Python interface. There is a separate API and Python package for accessing PV_Live modelled outturn estimates: [github.com/SheffieldSolar/PV_Live-API](https://github.com/SheffieldSolar/PV_Live-API).

Subscribing to the higher spatial resolution forecasts will also give access to the lower resolution ones i.e. subscribing to the PES-level forecasts also gives access to the national forecasts while subscribing to the GSP-level forecasts would give access to all three.


The Terms & Conditions for the service are available [here](https://api.solar.sheffield.ac.uk/pvforecast/tandc).

## How do I get set up?

* Make sure you have Git installed - [Download Git](https://git-scm.com/downloads)
* Run `pip install git+https://github.com/SheffieldSolar/PV_Forecast-API`
* You will need a _User ID_ and _API Key_ for Sheffield Solar's PV_Forecast service - log in to the [PV_Forecast API website](https://api.solar.sheffield.ac.uk/pvforecast/) and go to the [User Area](https://api.solar.sheffield.ac.uk/pvforecast/user) to find yours.

## Usage

There are three methods for extracting raw data from the PV_Forecast API:

|Method|Description|Docs Link|
|------|-----------|---------|
|`PVForecast.latest(entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get the latest PV forecast from the API.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.latest)|
|`PVForecast.get_forecast(forecast_base_gmt=None, entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get the PV forecast for a given forecast base from the API.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.get_forecast)|
|`PVForecast.get_forecasts(start, end, forecast_base_times=[], entity_type="pes", entity_id=0, extra_fields="", dataframe=False)`|Get all PV forecasts during a given time interval from the API.|[&#128279;](https://sheffieldsolar.github.io/PV_Forecast-API/build/html/modules.html#pvforecast_api.pvforecast.PVForecast.get_forecasts)|

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

from pvforecast_api import PVForecast

pvf = PVForecast(user_id="", api_key="") # Enter your user_id and api_key here!
```

|Example|Code|Example Output|
|-------|----|------|
|Get the latest nationally aggregated GB PV outturn forecast|`pvf.latest()`|`[[0, '2021-02-23T10:00:00Z', '2021-02-23T10:30:00Z', 2600.0], ..., [0, '2021-02-23T10:00:00Z', '2021-02-26T10:00:00Z', 5230.0]]`|
|Get the latest aggregated outturn forecast for **PES** region **23** (Yorkshire) as a DataFrame|`pvf.latest(entity_id=23, dataframe=True)`|![Screenshot of output](/misc/code_example_output1.png?raw=true)
|Get the latest aggregated outturn forecast for **GSP** ID **152** (INDQ1 or "Indian Queens")|`pvf.latest(entity_type="gsp", entity_id=152, dataframe=True)`|![Screenshot of output](/misc/code_example_output2.png?raw=true)
|Get the nationally aggregated GB PV outturn forecast with forecast base `2021-02-23T07:00:00Z` as a DataFrame|`pvf.get_forecast(datetime(2021, 2, 23, 7, 0, tzinfo=pytz.utc), dataframe=True))`|![Screenshot of output](/misc/code_example_output3.png?raw=true)|
|Get all 07:00 nationally aggregated GB PV outturn forecasts between `2021-02-23T01:00:00Z` and `2021-02-23T07:00:00Z`, as a DataFrame|`pvf.get_forecasts(datetime(2021, 2, 23, 1, 0, tzinfo=pytz.utc), datetime(2021, 2, 23, 7, 0, tzinfo=pytz.utc), forecast_base_times=["07:00"], dataframe=True))`|![Screenshot of output](/misc/code_example_output4.png?raw=true)|

## Command Line Utilities

### pvforecast

This utility can be used to download data to a CSV file:

```
usage: pvforecast.py [-h] --user_id <user_id> [--api_key <api_key>]
                     [-s "<yyyy-mm-dd HH:MM:SS>"] [-e "<yyyy-mm-dd HH:MM:SS>"]
                     [--entity_type <entity_type>] [--entity_id <entity_id>]
                     [-q] [-o </path/to/output/file>] [-http <http_proxy>]
                     [-https <https_proxy>]

This is a command line interface (CLI) for the PVForecast API module

optional arguments:
  -h, --help            show this help message and exit
  --user_id <user_id>   PVForecast user id.
  --api_key <api_key>   Your PVForecast API key. If not path passed, will
                        check environment variables for `PVForecastAPIKey` and
                        finally a config file in same directory named
                        `.pvforecast_credentials`
  -s "<yyyy-mm-dd HH:MM:SS>", --start "<yyyy-mm-dd HH:MM:SS>"
                        Specify a UTC start date in 'yyyy-mm-dd HH:MM:SS'
                        format (inclusive), default behaviour is to retrieve
                        the latest outturn.
  -e "<yyyy-mm-dd HH:MM:SS>", --end "<yyyy-mm-dd HH:MM:SS>"
                        Specify a UTC end date in 'yyyy-mm-dd HH:MM:SS' format
                        (inclusive), default behaviour is to retrieve the
                        latest outturn.
  --entity_type <entity_type>
                        Specify an entity type, either 'gsp' or 'pes'. Default
                        is 'gsp'.
  --entity_id <entity_id>
                        Specify an entity ID, default is 0 (i.e. national).
  -q, --quiet           Specify to not print anything to stdout.
  -o </path/to/output/file>, --outfile </path/to/output/file>
                        Specify a CSV file to write results to.
  -http <http_proxy>, -http-proxy <http_proxy>
                        HTTP Proxy address
  -https <https_proxy>, -https-proxy <https_proxy>
                        HTTPS Proxy address

Jamie Taylor & Ethan Jones, 2022-12-10
```

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
