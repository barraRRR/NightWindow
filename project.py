import sys
import os
from time import sleep
import requests
import json
import functools
from readchar import readkey
from geopy.geocoders import Nominatim
from datetime import datetime, timezone, timedelta
from PIL import Image
import ascii_magic
from skysimulator import SkySimulator, Spinner


def main() -> None:
    print(LOGO)
    sleep(1.5)

    while True:
        clear()
        menu()
        lat, lon, city = get_coords()
        date = get_date()
        if not summary(lat, lon, city, date):
            continue
        clear()
        sim = SkySimulator(lat=lat, lon=lon, t_utc=date)
        create_gallery(start_time=date,
                    sim=sim,
                    total_frames=331,
                    minutes_step=2)
        filename = get_filename(date, city)
        create_gif(duration=80, output_name=filename)
        print(TEXTS['status']['gif_created'])
        end()


def with_spinner(msg_key: str, success_key: str = None, delay: float = 0.5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            load_msg = TEXTS['status'].get(msg_key, 'Loading...')
            
            with Spinner(load_msg):
                result = func(*args, **kwargs)

                if delay > 0:
                    sleep(delay)
                
                if success_key:
                    success_msg = TEXTS['status'].get(success_key, 'Done!')
                    print(f'{success_msg}')
            return result
        return wrapper
    return decorator


def load_texts(language: str) -> dict:
    filename = f'{language}_texts.json'
    try:
        with open(filename, 'r', encoding='utf-8') as data:
            return json.load(data)

    except Exception:
        sys.exit('❌ Error: text file not found')


@with_spinner(msg_key='init', delay=2.0)
def welcome() -> str:
    os.system('cls' if os.name == 'nt' else 'clear')    
    try:
        with open('title.txt', 'r', encoding='utf-8') as file:
            logo = file.read()
            sleep(2)

    except FileNotFoundError:
        sys.exit('Error: title.txt not found')
    
    return logo


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)


def app_exit() -> None:
    clear()
    sys.exit(TEXTS['ui']['exit'])


def get_option(msg: str, options: list[str]) -> str:
    print(msg)
    for i, option in enumerate(options, start=1):
        print(f'   [{i}] - {option}') 
    print('   [q] - Quit')

    while True:
        try:
            key = readkey().lower()
            if key == 'q':
                app_exit()            
            selection = int(key)
            if 1 <= selection <= len(options):
                return key
            raise ValueError(
                TEXTS['errors']['invalid_option']
                )
        except ValueError as e:
            print('\n', e)


def menu() -> None:
    while True:
        user_choice = get_option(
            TEXTS['ui']['menu_select'], [
                TEXTS['ui']['menu_start'],
                TEXTS['ui']['menu_help']
                ])
        
        if user_choice == '1':
            break
        elif user_choice == '2':
            clear()
            print(TEXTS['ui']['instructions'])
            while True:
                key = readkey().lower()
                if key == '\n':
                    clear()
                    break
                elif key == 'q':
                    app_exit()
                continue
            continue
    clear()


def get_coords() -> tuple[float, float, str]:
    user_input = get_option(
        TEXTS['ui']['prompt_location'], [
            TEXTS['ui']['opt_ip'],
            TEXTS['ui']['opt_city']
        ])


    if user_input == '1':
        try:
            response = requests.get('http://www.ip-api.com/json', timeout=5)
            response.raise_for_status()
            data = response.json()
            coords = (data['lat'], data['lon'], data['city'])

        except Exception as e:
            sys.exit(e)

    elif user_input == '2':
        while True:
            geolocator = Nominatim(user_agent='star_chart_app')
            try:
                city_name = input('\n' + TEXTS['ui']['enter_city'])
                if city_name == 'quit':
                    app_exit()
                
                location = geolocator.geocode(city_name)
                if location:
                    coords = (location.latitude, location.longitude, city_name)
                    break
                else:
                    raise Exception
            
            except Exception:
                print('\n' + TEXTS['errors']['invalid_city'])
    
    clear()
    return coords


def get_date() -> datetime:
    user_input = get_option(
    TEXTS['ui']['prompt_date'], [
        TEXTS['ui']['opt_tonight'],
        TEXTS['ui']['opt_custom_date']]
    )

    if user_input == '1':
        date = datetime.now(timezone.utc)
    else:
        while True:
            try:
                date = datetime.fromisoformat(
                    input('\n' + TEXTS['ui']['enter_date'])
                    )
                break
            except Exception:
                print(TEXTS['errors']['date'] + '\n')
    
    clear()
    return date.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def summary(lat: float, lon: float, city: str, date: datetime) -> bool:
    sum = TEXTS['ui']['summary'].format(lat=lat, lon=lon, city=city, date=date.strftime('%Y-%m-%d'))
    print(sum)
    print(TEXTS['ui']['window_confirm'])

    while True:
        key = readkey().lower()
        if key == '\n':
            clear()
            return True
        elif key == 'b':
            return False
        elif key == 'q':
            app_exit()
    

def create_gallery(start_time: datetime,
                   sim: SkySimulator,
                   total_frames: int = 200,
                   minutes_step: int = 2) -> None:
    print(TEXTS['status']['starting_sim'].format(time=start_time.strftime('%H:%M')))
    for i in range(total_frames):
        current_time = start_time + timedelta(minutes=i * minutes_step)
        sim.generate_sky_frame(current_time=current_time, frame_num=i)
        render_ascii(f'frames/frame_{i:03d}.png')
        print(TEXTS['status']['frame_generated'].format(frame=f'{i:03d}', time=current_time.strftime('%H:%M')), end='\r')

    print(TEXTS['status']['sequence_completed'])


def render_ascii(img_path: str) -> None:
    try:
        ascii_art = ascii_magic.from_image(img_path)
        ascii_art.to_image_file(
            path=img_path,
            full_color=True,
            char=' ·*#@'
            )

    except Exception as e:
            print(TEXTS['errors']['ascii'])


def get_filename(date: datetime, city: str) -> str:
    safe_date = date.strftime('%Y%m%d')
    safe_city = city.strip().lower().replace(' ', '_')

    return f'nightwindow_{safe_date}_{safe_city}.gif'


@with_spinner(msg_key='creating_gif')
def create_gif(folder: str = 'frames',
               output_name: str = 'nightwindow.gif',
               duration: int = 150
               ) -> str:
    
    files = sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.endswith('.png')])
    if not files:
        raise FileNotFoundError(TEXTS['errors']['frames_not_found'])
    
    img, *append_images = [Image.open(f) for f in files]

    img.save(
        output_name,
        format='GIF',
        append_images=append_images,
        save_all=True,
        duration=duration,
        loop=0
    )

    output_path = os.path.abspath(output_name)
    return output_name


def end() -> None:
    print(TEXTS['ui']['end_prompt'])

    while True:
        key = readkey().lower()
        if key == '\n':
            break
        elif key == 'q':
            app_exit()


if __name__ == '__main__':
    TEXTS: dict = load_texts('en')
    LOGO: str = welcome()
    main()
