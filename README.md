# netatmo-to-json

This project writes data from your Netatmo weather station to a JSON file that can be read by PyMultimonAPRS https://asdil12.github.io/pymultimonaprs

### Getting Started
Get credentials from https://dev.netatmo.com/myaccount/createanapp and update the ```set_env.sh``` file with your credentials.

```
source set_env.sh
python3 fetch-netatmp.py
```

#### Weather file format
The format of the file as required by PyMultimonAPRS is as follows: 

```
{
	"timestamp": 1366148418,
	"wind": {
		"speed": 10,
		"direction": 240,
		"gust": 200
	},
	"temperature": 18.5,
	"rain": {
		"rainlast1h": 10,
		"rainlast24h": 20,
		"rainmidnight": 15
	},
	"humidity": 20,
	"pressure": 1013.25
}
```
Legend
```
    timestamp is seconds since epoch - must be included
    wind
        speed is in km/h
        direction is in deg
        gust is in km/h
    temperature is in °C
    rain
        rainlast1h is in mm
        rainlast24h is in mm
        rainmidnight is in mm
    humidity is in %
    pressure is in hPa
```

The timestamp must be included - everything else is optional.

