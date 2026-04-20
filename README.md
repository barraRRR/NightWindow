NightWindow 🌌
Your terminal portal to the stars.

NightWindow is a Python-based command-line tool that allows users to peer into the cosmos directly from their terminal. By leveraging real-time astronomical data and geolocation services, it generates a personalized star chart of the night sky and renders it as stunning ASCII art.

🛠 Features
Dual Geolocation: Automatically detect your location via IP address or manually search for any city worldwide using Geopy.

Real-time Star Charts: Connects to the AstronomyAPI to fetch precise celestial maps based on your coordinates and current date.

ASCII Rendering: Transforms high-resolution space imagery into terminal-friendly art using the ascii-magic library.

Clean Data Visualization: Utilizes a custom JSON configuration to filter out "noise" (grids and labels), providing a minimalist, star-only view.

Secure Credential Management: Implements .env file support and Base64 Basic Authentication to keep API secrets safe.

🚀 Installation
Clone the repository:

Bash
git clone https://github.com/yourusername/nightwindow.git
cd nightwindow
Create a Virtual Environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Setup your environment variables:
Create a .env file in the root directory and add your AstronomyAPI credentials:

Plaintext
CLIENT_ID='your_application_id'
CLIENT_SECRET='your_application_secret'
📖 Usage
Run the main script to open your window to the night sky:

Bash
python project.py
Upon execution, you will be prompted to:

Choose between using your current IP position or entering a specific city.

Wait while NightWindow calculates your coordinates, fetches the star chart, and processes the image.

View the final ASCII star map rendered directly in your terminal.

🧪 Testing
This project uses pytest to ensure logic consistency. To run the tests, execute:

Bash
pytest test_project.py
Tests cover:

Coordinate range validation.

Base64 authentication token generation.

JSON payload construction logic.

📂 Project Structure
project.py: The main application logic.

test_project.py: Unit tests for core functions.

config.json: Base parameters for the Star Chart API (visibility, zoom, styles).

.env: (Ignored by git) Private API keys.

requirements.txt: List of necessary Python libraries.

📜 Acknowledgments
AstronomyAPI for the celestial data.

OpenStreetMap (Nominatim) for geocoding services.

CS50P staff for the inspiration and Python fundamentals.

Author

Developed as a Final Project for CS50’s Introduction to Programming with Python.





SOlo cubre hasta 2050