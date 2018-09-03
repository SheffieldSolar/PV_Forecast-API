# PV_Forecast-API
A Python implementation of the PV_Forecast web API. See [www.solar.sheffield.ac.uk/pvforecast/](https://www.solar.sheffield.ac.uk/pvforecast/) and [api.solar.sheffield.ac.uk](https://api.solar.sheffield.ac.uk/)

## What is this repository for? ##

* A Python interface for the PV_Forecast web API to enable accessing PV_Forecast results in Python code.
* Version 0.1
* Works with Python 2.7+ or 3.5+

## How do I get set up? ##

* Make sure you have Git installed - [Download Git](https://git-scm.com/downloads)
* Run `pip install git+https://github.com/SheffieldSolar/PV_Forecast-API`
    - NOTE: You may need to run this command as sudo on Linux machines depending, on your Python installation i.e. `sudo pip install git+https://github.com/SheffieldSolar/PV_Forecast-API`

## Getting started ##

See [pvforecast_api_demo.py](https://github.com/SheffieldSolar/PV_Forecast-API/blob/master/pvforecast_api_demo.py) for example usage.
```Python
from pvforecast_api import PVForecast

pvf = PVForecast()
pvf.latest()
```

## Documentation ##

* [https://sheffieldsolar.github.io/PV_Forecast-API/](https://sheffieldsolar.github.io/PV_Forecast-API/)

## How do I upgrade? ##

Sheffield Solar will endeavour to update this library in sync with the [PV_Forecast API](https://api.solar.sheffield.ac.uk/pvforecast/ "PV_Forecast API webpage"), but cannot guarantee this. If you have signed up for an account on the PV_Forecast API platform then you will be notified by email in advance of any changes to the API.

To upgrade the code:
* Run `pip install --upgrade git+https://github.com/SheffieldSolar/PV_Forecast-API`

## Who do I talk to? ##

* Jamie Taylor - [jamie.taylor@sheffield.ac.uk](mailto:jamie.taylor@sheffield.ac.uk "Email Jamie") - [SheffieldSolar](https://github.com/SheffieldSolar)

## Authors ##

* **Jamie Taylor** - *Initial work* - [SheffieldSolar](https://github.com/SheffieldSolar)

## License ##

No license is defined yet - use at your own risk.
