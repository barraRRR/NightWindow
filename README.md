# NightWindow

**A Celestial Time-Lapse Generator for the Command Line**

[Video Demo](Your YouTube Link Here)

## Description
NightWindow is a Python-based CLI application that allows users to peer into the night sky from any location on Earth. By providing a city name or using their current IP, users can generate a beautiful, animated ascii GIF showing the movement of stars, planets, and the moon over the course of a night.



## Technical Features

### 1. The SkyEngine (Simulation)

Initially, the project was intended to use external Astronomy APIs. However, after realizing that third-party image outputs lacked the detail and customization needed for a smooth time-lapse, I shifted to a local rendering approach.

- **Skyfield**: Used to calculate precise celestial positions using the DE421 planetary ephemeris and the Hipparcos star catalog.
- **Matplotlib**: Acts as the rendering heart, plotting thousands of stars with magnitudes and colors, along with the Moon and visible planets (Mars, Jupiter, Saturn, Venus).
- **ASCII Magic**: Integrated to provide a unique "retro" aesthetic to the generated frames before compiling them.

### 2. Advanced UX/UI Components

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

- **Skyfield & Hipparcos Catalog** for the astronomical data.
- **CS50P Staff** for the foundations of Python development.

---

Enjoy your window to the stars! 🔭✨