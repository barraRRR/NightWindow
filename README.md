# 🌌 NightWindow

<div align="center">
<img width="1920" height="1080" alt="logo_white" src="https://github.com/user-attachments/assets/6038e0c8-375a-4eb2-a9e1-97337b7e87bb" />
</div>

**A Celestial Time-Lapse Generator for the Command Line**

[Video Demo](https://youtu.be/Z0Q9BfnsHI0)

## Description
NightWindow is a Python-based CLI application that allows users to peer into the night sky from any location on Earth. By providing a city name or using their current IP, users can generate a beautiful, animated ascii GIF showing the movement of stars, planets, and the moon over the course of a night.

<img width="1313" height="788" alt="nightwindow_20260422_madrid" src="https://github.com/user-attachments/assets/973aaa67-899d-4e46-9692-e96cea0fb1b0" />

## Technical Features

### 1. The SkyEngine (Simulation)

Initially, the project was intended to use external Astronomy APIs. However, after realizing that third-party image outputs lacked the detail and customization needed for a smooth time-lapse, I shifted to a local rendering approach.

- **Skyfield**: Used to calculate precise celestial positions using the DE421 planetary ephemeris and the Hipparcos star catalog.
- **Matplotlib**: Acts as the rendering heart, plotting thousands of stars with magnitudes and colors, along with the Moon and visible planets (Mars, Jupiter, Saturn, Venus).
- **ASCII Magic**: Integrated to provide a unique "retro" aesthetic to the generated frames before compiling them.

### 2. The Rendering Engine (Matplotlib)

While Matplotlib is traditionally used for data visualization, NightWindow repurposes it as a graphical render engine to generate high-fidelity celestial frames.

Key technical implementations include:

- **Dynamic Star Sizing**: Instead of uniform points, star sizes are calculated using an exponential formula based on their Hipparcos magnitude. This mimics real-world luminosity, where brighter stars appear larger on a black background.
  - Formula: `s = ((6 - magnitude) ** 2.5) + 20`

- **Horizon Masking**: The engine performs real-time filtering of astronomical coordinates. Only objects with an altitude >0° are passed to the scatter plot, ensuring stars and planets "set" naturally behind the horizon.

- **Planetary Color Mapping**: Specific hex-color values are assigned to major celestial bodies (e.g., #ff4500 for Mars, #f59aff for Jupiter) to maintain visual clarity and scientific recognition in the final output.

- **Fixed Viewport Configuration**: To create a consistent time-lapse, the engine locks the field of view (FOV) and axes limits. This prevents Matplotlib from auto-scaling, which is crucial for achieving a stable video effect in the final GIF.

- **Headless Rendering**: The class is optimized to run without a GUI backend (`plt.close()`), allowing for the rapid generation of hundreds of frames in the background without opening floating windows.

### 3. Advanced UX/UI Components

- **Threaded Spinner**: To prevent the CLI from feeling "frozen" during heavy astronomical calculations or API calls, I implemented a custom Spinner class. It runs on a background thread (threading), allowing a Braille animation to spin smoothly while the main thread processes data.
- **Custom Decorators**: I developed the `@with_spinner` decorator to wrap heavy-lifting functions. This keeps the code clean and provides a consistent visual feedback system (Loading → Success).
- **Single-Key Navigation**: Using the readchar library, the menu system responds to instant keypresses, eliminating the need for the user to press "Enter" after every selection.



## Architecture & Design Challenges

### The Circular Import Hurdle

One of the most significant technical challenges was managing the project's growth. As I modularized the code into `project.py`, `utils.py`, and `skysimulator.py`, I encountered a circular import error—the main script needed the utilities, but the utilities needed the global configuration and language strings.

**The Solution**: I refactored the architecture by creating a dedicated `config.py`. This file acts as a "Single Source of Truth," holding global constants, ASCII art, and the JSON-based internationalization system. This linearized the dependency graph and resolved the conflict.

## Project Structure

- **project.py**: The main execution flow and UI logic.
- **skysimulator.py**: The object-oriented engine for astronomy calculations and frame generation.
- **utils.py**: Reusable logic for the CLI (Spinners, decorators, file management).
- **config.py**: Global state and asset loading.
- **en_texts.json**: Centralized text dictionary for easy maintenance and future localization.



## Installation & Usage

### Prerequisites

- **Python 3.10+**
- **Dependencies** (install via `pip install -r requirements.txt`):
  - skyfield
  - matplotlib
  - requests
  - readchar
  - geopy
  - pillow
  - ascii_magic

### How to Run

1. Navigate to the project directory.
2. Run the application:
   ```bash
   python project.py
   ```
3. Choose your location method (IP or City).
4. Confirm the summary and wait for the "SkyEngine" to compile your night window.
5. Find your generated GIF in the root folder with the format: `nightwindow_YYYYMMDD_city.gif`.



## Reflections

This project allowed me to solidify my knowledge of Python's advanced features, particularly Multithreading and Decorators. Exploring the "Skeleton UX" flow helped me understand how a user interacts with a program, ensuring that even during long processing times, the interface remains engaging and informative. I truly enjoyed building a tool that turns cold, scientific data into a visual experience.


## Acknowledgments

- [Skyfield](https://github.com/skyfielders/python-skyfield/) - Astronomical position calculations and star catalog
- [Hipparcos Catalog](https://www.cosmos.esa.int/web/hipparcos) - Comprehensive star data
- [ASCII Magic](https://github.com/jmportilla/ascii_magic) - ASCII art conversion
- CS50P Staff - Foundations of Python development

---

Enjoy your window to the stars! 🔭✨
