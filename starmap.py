from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import os


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

        astrometric = observer.at(t).observe(self.stars)
        alt, az, d = astrometric.apparent().altaz()

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        mask = alt.degrees > 0
        ax.scatter(
            az.radians[mask],
            90 - alt.degrees[mask],
            s=(6 - self.stars_df['magnitude'][mask]) ** 2, # Tamaño basado en brillo
            c='white',
            edgecolors='none'
            )
        
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.axis('off')

        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        filename = f'frames/frame_{frame_num:03d}.png'

        plt.savefig(filename, facecolor='black', bbox_inches='tight', pad_inches=0)
        plt.close()


def test() -> None:

    sim = SkySimulator()
    lat, lon = 40.4167, -3.7033
    start_time = datetime.now(timezone.utc).replace(
        hour=21,
        minute=0,
        second=0,
        microsecond=0
    )

    total_frames = 24 * 3
    minutes_step = 10

    print(f'🎬 Iniciando simulación desde las {start_time.strftime("%H:%M")} UTC...')
    for i in range(total_frames):
        current_time = start_time + timedelta(minutes=i * minutes_step)
        sim.generate_sky_frame(lat, lon, current_time, i)
        print(f'Frame {i:03d} generado para las {current_time.strftime("%H:%M")}', end='\r')

    print('\n✅ ¡Secuencia completada!')


if __name__ == '__main__':
    test()
