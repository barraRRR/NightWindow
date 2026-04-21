import sys
import os
import time
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timezone, timedelta
from PIL import Image
import ascii_magic
from utils import IpError, GeolocationError, AstronomyAPIError
from utils import loading, app_exit, get_option, welcome
from starmap import SkySimulator


def main() -> None:
    welcome()
    lat, lon, city = get_coords()
    start_time = get_date()
    sim = SkySimulator(lat=lat, lon=lon, t_utc=start_time)
    create_gallery(start_time=start_time,
                   sim=sim,
                   total_frames=200,
                   minutes_step=2)
    create_gif()


def create_gallery(start_time: datetime,
                   sim: SkySimulator,
                   total_frames: int = 200,
                   minutes_step: int = 2) -> None:
    print(f'🎬 Iniciando simulación desde las {start_time.strftime("%H:%M")} UTC...')
    for i in range(total_frames):
        current_time = start_time + timedelta(minutes=i * minutes_step)
        sim.generate_sky_frame(current_time=current_time, frame_num=i)
        render_ascii(f'frames/frame_{i:03d}.png')
        print(f'Frame {i:03d} generado para las {current_time.strftime("%H:%M")}', end='\r')

    print('\n✅ ¡Secuencia completada!')


def get_date() -> datetime:
        user_input = get_option(
        'Choose option:', [
            'Tonight',
            'Another date']
        )

        try:
            if user_input == '1':
                date = datetime.now(timezone.utc)
            else:
                date = datetime.fromisoformat(
                    input('Enter date (YYYY-MM-DD): ')
                    )
        except Exception:
            sys.exit('Error: an error ocurred when retrieving date')
        
        return date.replace(hour=19, minute=0, second=0, microsecond=0)


def get_coords() -> tuple[float, float, str]:
    user_input = get_option(
        'Please, select your choice of preference:', [
            'my current position [ip]',
            'introduce location'
        ])

    try:
        if user_input == '1':
            response = requests.get('http://www.ip-api.com/json', timeout=5)
            response.raise_for_status()
            data = response.json()
            return data['lat'], data['lon'], data['city']
        elif user_input == '2':
            city_name = input('Enter city name: ')
            geolocator = Nominatim(user_agent='star_chart_app')
            location = geolocator.geocode(city_name)
            if location:
                return location.latitude, location.longitude, city_name
    
    except (IpError, GeolocationError) as e:
        sys.exit(e)


def create_gif(folder: str = 'frames',
               output_name: str = 'NightWindow.gif',
               duration: int = 150
               ) -> str:
    
    print(f'🎞️ Creating GIF: {output_name}...')

    files = sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.endswith('.png')])
    if not files:
        raise FileNotFoundError('Frames not found')
    
    img, *append_images = [Image.open(f) for f in files]

    img.save(
        output_name,
        format='GIF',
        append_images=append_images,
        save_all=True,
        duration=duration,
        loop=0
    )

    print('GIF succesfully created')

    return output_name


def render_ascii(img_path: str) -> None:
    try:
        ascii_art = ascii_magic.from_image(img_path)
        ascii_art.to_image_file(
            path=img_path,
            full_color=True,
            char=' ·*#@'
            )

    except Exception as e:
            print(f'Error rendering ASCII: {e}')


if __name__ == '__main__':
    main()
