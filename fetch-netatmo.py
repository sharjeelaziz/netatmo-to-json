#!/usr/bin/env python
import os
import sys
import json
import time
import requests


def get_token(payload):
    try:
        resp = requests.post('https://api.netatmo.com/oauth2/token', data=payload)
        if resp.status_code == 200:
            token = resp.json()
            token['expiry'] = int(time.time()) + token['expires_in']
        else:
            token = None
            print('get_token failed! are the environment variable set?')
    except requests.exceptions.ProxyError as error:
        print('Proxy error', error.response)
    except requests.exceptions.RequestException as error:
        print('Request error: ', error.response)
    return token


def update_file(token, netatmo_client_id, netatmo_client_secret):
    # Check if token needs refresh
    if token['expiry'] - int(time.time()) < 600:
        try:
            data = dict(grant_type='refresh_token', refresh_token=token['refresh_token'], client_id=netatmo_client_id,
                        client_secret=netatmo_client_secret)
            resp = requests.post('https://api.netatmo.com/oauth2/token', data=data)
            if resp.status_code == 200:
                token = resp.json()
                token['expiry'] = int(time.time()) + token['expires_in']
        except requests.exceptions.ProxyError as error:
            print('Proxy error', error.response)
        except requests.exceptions.RequestException as error:
            print('Request error: ', error.response)
        print('refreshing token!')

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
                    module_dashboard = module['dashboard_data']

                    if module_type == 'NAModule1':  # Outdoor
                        weather['temperature'] = module_dashboard['Temperature']
                        weather['humidity'] = module_dashboard['Humidity']

                    if module_type == 'NAModule3':  # Rain
                        if 'sum_rain_1' in module_dashboard:
                            rain['rainlast1h'] = module_dashboard['sum_rain_1']
                        if 'sum_rain_24' in module_dashboard:
                            rain['rainlast24h'] = module_dashboard['sum_rain_24']
                        weather['rain'] = rain

                    if module_type == 'NAModule2':  # Wind
                        wind['speed'] = module_dashboard['WindStrength']
                        wind['direction'] = module_dashboard['WindAngle']
                        wind['gust'] = module_dashboard['GustStrength']
                        weather['wind'] = wind

            base_path = os.path.dirname(os.path.realpath(__file__))
            filename = os.path.join(base_path, 'weather.json')
            json_file = json.dumps(weather, indent=4)
            print(json_file)

            weather_file = open(filename, "w")
            weather_file.write(json_file)
            weather_file.close()

    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)
    except KeyError as error:
        print('error.message')


def main():
    # https://dev.netatmo.com/
    netatmo_client_id = os.getenv('NETATMO_CLIENT_ID')
    netatmo_client_secret = os.getenv('NETATMO_CLIENT_SECRET')
    netatmo_username = os.getenv('NETATMO_USERNAME')
    netatmo_password = os.getenv('NETATMO_PASSWORD')

    payload = dict(grant_type='password', client_id=netatmo_client_id,
                client_secret=netatmo_client_secret, username=netatmo_username,
                password=netatmo_password, scope='read_station')

    token = get_token(payload)

    while True:
        if token is not None and 'expiry' in token:
            update_file(token, netatmo_client_id, netatmo_client_secret)
        else:
            token = get_token(payload)
        time.sleep(480)


if __name__ == '__main__':
    main()
