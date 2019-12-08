#!/usr/bin/env python
import os
import sys
import json
import time
import requests


def get_token(my_data):

    try:
        resp = requests.post('https://api.netatmo.com/oauth2/token', data=my_data)
        if resp.status_code == 200:
            token = resp.json()
            token['expiry'] = int(time.time()) + token['expires_in']
    except requests.exceptions.ProxyError as error:
        print("Proxy error", error.response)
    except requests.exceptions.RequestException as error:
        print("Request error: ", error.response)
    return token


def update_file(token):

    # Check if token needs refresh
    if token['expiry'] - int(time.time()) < 600:
        try:
            data = dict(grant_type='refresh_token', refresh_token=token['refresh_token'], client_id=NETATMO_CLIENT_ID,
                        client_secret=NETATMO_CLIENT_SECRET)
            resp = requests.post('https://api.netatmo.com/oauth2/token', data=data)
            if resp.status_code == 200:
                token = resp.json()
                token['expiry'] = int(time.time()) + token['expires_in']
        except requests.exceptions.ProxyError as error:
            print("Proxy error", error.response)
        except requests.exceptions.RequestException as error:
            print("Request error: ", error.response)

    try:
        resp = requests.get('https://api.netatmo.com/api/getstationsdata?access_token=' + token['access_token'])
        if resp.status_code == 200:
            data = resp.json()
            weather = {}
            wind = {}
            rain = {}

            for device in data['body']['devices']:
                weather['timestamp'] = device['dashboard_data']['time_utc']
                weather['pressure'] = device['dashboard_data']['Pressure']

                for module in device['modules']:
                    module_type = module['type']

                    if module_type == 'NAModule1':  # Outdoor
                        weather['temperature'] = module['dashboard_data']['Temperature']
                        weather['humidity'] = module['dashboard_data']['Humidity']

                    if module_type == 'NAModule3':  # Rain
                        rain['rainlast1h'] = module['dashboard_data']['sum_rain_1']
                        rain['rainlast24h'] = module['dashboard_data']['sum_rain_24']
                        weather['rain'] = rain

                    if module_type == 'NAModule2':  # Wind
                        wind['speed'] = module['dashboard_data']['WindStrength']
                        wind['direction'] = module['dashboard_data']['WindAngle']
                        wind['gust'] = module['dashboard_data']['GustStrength']
                        weather['wind'] = wind
            json_file = json.dumps(weather, indent=4)
            print(json_file)

            weather_file = open("weather.json", "w")
            weather_file.write(json_file)
            weather_file.close()

    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)


def main():

    # https://dev.netatmo.com/
    NETATMO_CLIENT_ID = os.getenv('NETATMO_CLIENT_ID')
    NETATMO_CLIENT_SECRET = os.getenv('NETATMO_CLIENT_SECRET')
    NETATMO_USERNAME = os.getenv('NETATMO_USERNAME')
    NETATMO_PASSWORD = os.getenv('NETATMO_PASSWORD')

    data = dict(grant_type='password', client_id=NETATMO_CLIENT_ID,
                client_secret=NETATMO_CLIENT_SECRET, username=NETATMO_USERNAME,
                password=NETATMO_PASSWORD, scope='read_station')

    while True:
        token = get_token(data)
        update_file(token)

        time.sleep(480)


if __name__ == "__main__":
    main()
