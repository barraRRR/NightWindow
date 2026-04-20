from time import sleep
import os
import sys
from readchar import readkey


class AppError(Exception):
    pass


class IpError(AppError):
    def __str__(self):
        return 'Error: IP error related'


class GeolocationError(AppError):
    def __str__(self):
        return 'Error: geolocation has failed'


class AstronomyAPIError(AppError):
    def __str__(self):
        return 'Error: AstronomyAPI has failed'


def loading(msg: str = 'loading', points: int = 5, delay: int = 3) -> None:
    print('\n', msg, end='')
    for _ in range(points):
        sleep(1)
        print('.', end='', flush=True)
    sleep(delay)


def app_exit() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit('\nThanks for using NightWindow\n')


def get_option(msg: str, options: list[str]) -> str:
    print(msg)
    for i, option in enumerate(options, start=1):
        print(f'   [{i}] - {option}') 
    print('   [q] - quit')

    while True:
        try:
            key = readkey().lower()
            if key == 'q':
                app_exit()            
            selection = int(key)
            if 1 <= selection <= len(options):
                os.system('cls' if os.name == 'nt' else 'clear')
                return key
            raise ValueError(
                'Invalid option. Please, choose one valid option'
                )
        except ValueError as e:
            print('\n', e)

def welcome() -> None:
    loading('Initializing NightWindow', delay=1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print('\n\n\n')
    
    try:
        with open('title.txt', 'r', encoding='utf-8') as title:
            print(title.read())
            sleep(2)
    except FileNotFoundError:
        sys.exit('Error: title.txt not found')
