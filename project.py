import sys
import os
import time
import requests
from geopy.geocoders import Nominatim
from ascii_magic import AsciiArt, Back
import json
from utils import IpError, GeolocationError, AstronomyAPIError
from utils import loading, app_exit, get_option, welcome
from starmap import SkySimulator


def main() -> None:
    #welcome()
    user_input = get_option(
        'Please, select your choice of preference:', [
            'my current position [ip]',
            'introduce location'
        ])

    try:
        if user_input == '1':
            data = get_coords('ip')
        elif user_input == '2':
            data = get_coords(input('Enter city name: '))
    
    except (IpError, GeolocationError) as e:
        sys.exit(e)
    
    lat, lon, city = data
    client_id, client_secret = load_creadentials()

    auth_code = get_auth_code(client_id, client_secret)
    star_char = get_star_char(lat, lon, '2026-04-20', auth_code)
    display_star_char(star_char)


def get_coords(city_name: str) -> tuple[float, float, str]:
    try:
        if city_name == 'ip':
            response = requests.get('http://www.ip-api.com/json', timeout=5)
            response.raise_for_status()
            data = response.json()
            return data['lat'], data['lon'], data['city']
        
        else:
            geolocator = Nominatim(user_agent='star_chart_app')
            location = geolocator.geocode(city_name)
            if location:
                return location.latitude, location.longitude, city_name
    
    except Exception as e:
            sys.exit(e)




if __name__ == '__main__':
    main()
