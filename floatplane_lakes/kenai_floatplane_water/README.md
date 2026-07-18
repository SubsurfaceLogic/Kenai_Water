# Kenai Floatplane Lake Identifier

"""
Kenai Floatplane Lake Identifier
Created by: Me
AI Assistance: Developed with support from Google Gemini for GEE API integration.
"""


An automated GIS tool to identify water bodies on the Kenai Peninsula suitable for floatplane operations based on pilot safety constraints.

## Constraints
Calculated using Google Earth Engine (Sentinel-2 & SRTM):
* **Minimum Length:** 800m
* **Minimum Width:** 40m
* **Maximum Elevation:** 760m

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Authenticate with Google Earth Engine: `earthengine authenticate`
4. Run the script: `python main.py`

## Known Issues
* **Elevation Data:** Currently, the elevation property is not working effectively

## License
MIT License