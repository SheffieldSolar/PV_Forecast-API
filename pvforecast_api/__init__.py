try:
    #py2
    from pvforecast import PVForecast
except:
    #py3+
    from pvforecast_api.pvforecast import PVForecast

__all__ = ["PVForecast"]
