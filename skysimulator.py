from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import matplotlib.pyplot as plt
from datetime import datetime
import os
import warnings


warnings.filterwarnings('ignore', category=RuntimeWarning)


class SkySimulator:
    """
    Astronomical simulator for generating night sky frames.
    Calculates celestial positions of stars, planets, and the moon for a given location and time.
    Renders frames using Matplotlib with customizable magnitude limits.
    """
    def __init__(self,
                 lat: float,
                 lon: float,
                 t_utc: datetime,
                 mag_limit: float = 5.0):
        """
        Initialize the SkySimulator with observer location and observation time.
        
        Args:
            lat (float): Observer latitude in degrees (-90 to 90)
            lon (float): Observer longitude in degrees (-180 to 180)
            t_utc (datetime): Observation time in UTC
            mag_limit (float): Magnitude limit for visible stars (default: 5.0, lower = dimmer stars hidden)
        """
        self.mag_limit = mag_limit
        self.lat = lat
        self.lon = lon
        self.t_utc = t_utc
        
    def load_assets(self) -> None:
        """
        Load astronomical data: ephemeris, planetary data, and star catalog.
        Downloads and caches Skyfield data (DE421 ephemeris and Hipparcos catalog).
        Populates instance variables: ts (timescale), planets, earth, stars_df, stars.
        """
        if not os.path.exists('de421.bsp') or not os.path.exists('hip_main.dat'):
            from config import TEXTS
            print(TEXTS['status']['load_data'])
        
        self.ts = load.timescale()
        self.planets = load('de421.bsp')     
        self.earth = self.planets['earth']

        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        self.stars_df = df[df['magnitude'] <= self.mag_limit]
        self.stars = Star.from_dataframe(self.stars_df)
    
    def generate_sky_frame(
            self,
            current_time: datetime,
            frame_num: int = 0
            ) -> None:
        """
        Generate a single sky frame (PNG image) for the given time.
        Renders stars (with magnitude-based sizing), visible planets, and the moon.
        
        Args:
            current_time (datetime): The observation time for this frame
            frame_num (int): Frame sequence number for filename (default: 0)
            
        Returns:
            None: Saves PNG file to 'frames/frame_XXXX.png'
        """
        
        observer = self.earth + wgs84.latlon(self.lat, self.lon)
        t = self.ts.from_datetime(current_time)

        astrometric_stars = observer.at(t).observe(self.stars)
        alt_s, az_s, _ = astrometric_stars.apparent().altaz()

        moon = self.planets['moon']
        astrometric_moon = observer.at(t).observe(moon)
        alt_m, az_m, _ = astrometric_moon.apparent().altaz()

        planets_to_draw = {
            'mars': '#ff4500',
            'jupiter barycenter': "#f59aff",
            'saturn barycenter': "#fe9000",
            'venus': "#dd57ff"
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        mask_s = alt_s.degrees > 0
        ax.scatter(
            az_s.degrees[mask_s],
            alt_s.degrees[mask_s],
            s=((6 - self.stars_df['magnitude'][mask_s]) ** 2.5) + 20,
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
                    s=120,
                    c=color, 
                    edgecolors='white',
                    linewidth=0.5,
                    label=name.capitalize()
                )
        
        if alt_m.degrees > 0:
            ax.scatter(
                az_m.degrees, 
                alt_m.degrees, 
                s=600,
                c='#FFFACD',
                edgecolors='white',
                alpha=0.9,
                marker='o'
            )
        
        center_az = 280
        fov_width = 100
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
