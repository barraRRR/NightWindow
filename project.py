import sys
import os
from time import sleep
import requests
from readchar import readkey
from geopy.geocoders import Nominatim
from datetime import datetime, timezone, timedelta
from PIL import Image
import ascii_magic
from skysimulator import SkySimulator
from utils import Spinner, with_spinner, clear, end
from utils import get_option, app_exit
from config import TEXTS, LOGO


def main() -> None:
    """
    Main entry point of the application. Orchestrates the entire workflow:
    displays welcome screen, manages user menu, collects location and date,
    creates astronomical simulation, generates frame gallery, and compiles GIF.
    """
    welcome()

    while True:
        clear()
        menu()
        lat, lon, city = get_coords()
        date = get_date()
        if not summary(lat, lon, city, date):
            continue
        sim = create_simulator(lat=lat, lon=lon, date=date)
        create_gallery(start_time=date,
                    sim=sim,
                    total_frames=331,
                    minutes_step=2)
        filename = get_filename(date, city)
        create_gif(duration=80, output_name=filename)
        print(TEXTS['status']['gif_created'].format(path=os.path.abspath(filename)))
        end()


def welcome() -> str:
    """
    Display the welcome screen with the application logo and a brief delay.
    Clears the terminal and shows the NightWindow logo.
    """
    os.system('cls' if os.name == 'nt' else 'clear')    
    @with_spinner(msg_key='init', delay=1.0)
    def show_logo() -> str:
        return LOGO
    
    show_logo()
    print(LOGO)
    sleep(1.5)


def menu() -> None:
    """
    Display the main menu allowing users to start or access help.
    Handles navigation between start and help options.
    """
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
    """
    Retrieve geographic coordinates (latitude, longitude, city name).
    Allows user to choose between IP-based geolocation or manual city search.
    
    Returns:
        tuple[float, float, str]: A tuple containing (latitude, longitude, city_name)
    """
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
            sys.exit(TEXTS['errors']['api_timeot'])

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
    """
    Retrieve the observation date from user input.
    Allows user to choose between tonight or a custom date.
    
    Returns:
        datetime: A datetime object set to 21:00 UTC on the selected date.
    """
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
    """
    Display a summary of selected parameters and ask for user confirmation.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        city (str): City name
        date (datetime): Observation date
        
    Returns:
        bool: True if user confirms, False if user chooses to go back.
    """
    @with_spinner(msg_key='confirming_target', success_key='target_confirmed', delay=1.5)
    def show_sum() -> str:
        sum = TEXTS['ui']['summary'].format(lat=lat, lon=lon, city=city, date=date.strftime('%Y-%m-%d'))
        return f'{sum}\n{TEXTS['ui']['window_confirm']}'
    
    sum_text = show_sum()
    sleep(1)
    print('\n' + sum_text)
    while True:
        key = readkey().lower()
        if key == '\n':
            clear()
            return True
        elif key == 'b':
            clear()
            return False
        elif key == 'q':
            app_exit()


def create_simulator(lat: float, lon: float, date: datetime) -> SkySimulator:
    """
    Create and initialize a SkySimulator instance with the given parameters.
    Loads astronomical data including planets, stars, and ephemeris.
    
    Args:
        lat (float): Observer latitude
        lon (float): Observer longitude
        date (datetime): Reference date for simulation
        
    Returns:
        SkySimulator: Initialized simulator instance ready for frame generation.
    """
    try:
        @with_spinner('loading_engine', delay=1.0)
        def get_sim() -> SkySimulator:
            return SkySimulator(lat=lat, lon=lon, t_utc=date)
        
        sim = get_sim()
        sim.load_assets()

        clear()
    
    except Exception:
        sys.exit(TEXTS['errors']['database_error'])

    return sim
    

def create_gallery(start_time: datetime,
                   sim: SkySimulator,
                   total_frames: int = 200,
                   minutes_step: int = 2) -> None:
    """
    Generate a sequence of sky frames at regular time intervals.
    Each frame is rendered as an ASCII art representation.
    
    Args:
        start_time (datetime): Starting time for the time-lapse
        sim (SkySimulator): Initialized sky simulator instance
        total_frames (int): Total number of frames to generate (default: 200)
        minutes_step (int): Time interval between frames in minutes (default: 2)
    """
    @with_spinner(msg_key='starting_sim', success_key=' ', delay=1.5)
    def starting_text() -> str:
        return f'{TEXTS['status']['starting_sim'].format(time=start_time.strftime('%H:%M'))}'
    
    starting_text()
    for i in range(total_frames):
        current_time = start_time + timedelta(minutes=i * minutes_step)
        sim.generate_sky_frame(current_time=current_time, frame_num=i)
        render_ascii(f'frames/frame_{i:03d}.png')
        print(TEXTS['status']['frame_generated'].format(frame=f'{i:03d}', time=current_time.strftime('%H:%M')), end='\r')

    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()
    print(TEXTS['status']['sequence_completed'])
    sleep(1)
    clear()


def render_ascii(img_path: str) -> None:
    """
    Convert a PNG image to ASCII art representation and save it.
    Replaces the original image with an ASCII-rendered version.
    
    Args:
        img_path (str): Path to the PNG image file to convert.
    """
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
    """
    Generate a safe, formatted filename for the output GIF.
    Format: nightwindow_YYYYMMDD_city.gif
    
    Args:
        date (datetime): The observation date
        city (str): The city name
        
    Returns:
        str: A properly formatted filename string.
    """
    safe_date = date.strftime('%Y%m%d')
    safe_city = city.strip().lower().replace(' ', '_')

    return f'nightwindow_{safe_date}_{safe_city}.gif'


@with_spinner(msg_key='creating_gif')
def create_gif(folder: str = 'frames',
               output_name: str = 'nightwindow.gif',
               duration: int = 150
               ) -> str:
    """
    Compile PNG frames from a folder into an animated GIF.
    
    Args:
        folder (str): Path to folder containing PNG frames (default: 'frames')
        output_name (str): Output GIF filename (default: 'nightwindow.gif')
        duration (int): Frame duration in milliseconds (default: 150)
        
    Returns:
        str: The absolute path to the created GIF file.
    """
    
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


if __name__ == '__main__':
    main()
