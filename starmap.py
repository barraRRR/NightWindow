from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import os
from PIL import Image
import ascii_magic


class SkySimulator:
    def __init__(self, mag_limit: float = 5.0):
        print('🔭 Initializing Sky Engine...')
        self.mag_limit = mag_limit

        self.planets = load('de421.bsp')
        self.ts = load.timescale()
        self.earth = self.planets['earth']

        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        self.stars_df = df[df['magnitude'] <= self.mag_limit]
        self.stars = Star.from_dataframe(self.stars_df)
        print('✨ Assets loaded and ready.')

    def generate_sky_frame(
            self,
            lat: float,
            lon: float,
            t_utc: datetime,
            frame_num: int = 0
            ) -> None:
        
        observer = self.earth + wgs84.latlon(lat, lon)
        t = self.ts.from_datetime(t_utc)

        astrometric_stars = observer.at(t).observe(self.stars)
        alt_s, az_s, _ = astrometric_stars.apparent().altaz()

        moon = self.planets['moon']
        astrometric_moon = observer.at(t).observe(moon)
        alt_m, az_m, _ = astrometric_moon.apparent().altaz()

        planets_to_draw = {
            'mars': '#ff4500',    # Naranja rojizo
            'jupiter barycenter': "#f59aff", # Crema
            'saturn barycenter': "#fe9000",  # Dorado pálido
            'venus': "#dd57ff"    # Blanco brillante
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        mask_s = alt_s.degrees > 0
        ax.scatter(
            az_s.degrees[mask_s],
            alt_s.degrees[mask_s],
            s=((6 - self.stars_df['magnitude'][mask_s]) ** 2.5) + 20, # Tamaño basado en brillo
            c='white',
            edgecolors='white',
            alpha=1.0
            )
        
        for name, color in planets_to_draw.items():
            body = self.planets[name]
            astrometric_body = observer.at(t).observe(body)
            alt_p, az_p, _ = astrometric_body.apparent().altaz()

            if alt_p.degrees > 0:
                ax.scatter(
                    az_p.degrees, alt_p.degrees, 
                    s=120,          # Un poco más grandes que las estrellas
                    c=color, 
                    edgecolors='white',
                    linewidth=0.5,
                    label=name.capitalize()
                )
        
        if alt_m.degrees > 0:
            ax.scatter(
                az_m.degrees, 
                alt_m.degrees, 
                s=600,          # Mucho más grande que una estrella
                c='#FFFACD',    # Un color crema/luna
                edgecolors='white',
                alpha=0.9,
                marker='o'      # Un círculo perfecto
            )
        
        center_az = 280  # Este
        fov_width = 100  # Ancho de la ventana
        ax.set_xlim(center_az - fov_width/2, center_az + fov_width/2)
        ax.set_ylim(0, 60)
        ax.axis('off')

        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        filename = f'frames/frame_{frame_num:03d}.png'

        plt.savefig(
            filename,
            facecolor='black',
            bbox_inches='tight',
            pad_inches=0
            )
        plt.close()


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


def test() -> None:

    sim = SkySimulator()
    lat, lon = 40.4167, -3.7033
    start_time = datetime.now(timezone.utc).replace(
        hour=19,
        minute=0,
        second=0,
        microsecond=0
    )

    total_frames = 200
    minutes_step = 2

    print(f'🎬 Iniciando simulación desde las {start_time.strftime("%H:%M")} UTC...')
    for i in range(total_frames):
        current_time = start_time + timedelta(minutes=i * minutes_step)
        sim.generate_sky_frame(lat, lon, current_time, i)
        render_ascii(f'frames/frame_{i:03d}.png')
        print(f'Frame {i:03d} generado para las {current_time.strftime("%H:%M")}', end='\r')

    print('\n✅ ¡Secuencia completada!')

    create_gif()


if __name__ == '__main__':
    test()
