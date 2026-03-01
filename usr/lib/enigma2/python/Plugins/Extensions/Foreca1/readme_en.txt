# Foreca 1 Plugin Documentation for Enigma2

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Initial Configuration](#initial-configuration)
4. [Using the Plugin](#using-the-plugin)
   - [Main Screen](#main-screen)
   - [Main Menu](#main-menu)
   - [City Selection](#city-selection)
   - [Daily Forecast (7 days)](#daily-forecast-7-days)
   - [Meteogram](#meteogram)
   - [Observation Stations](#observation-stations)
   - [Weather Maps](#weather-maps)
   - [Unit Settings](#unit-settings)
   - [Color and Transparency](#color-and-transparency)
   - [Plugin Info](#plugin-info)
5. [Authenticated API Configuration (Optional)](#authenticated-api-configuration-optional)
6. [Troubleshooting](#troubleshooting)
7. [Credits](#credits)

---

## Introduction
**Foreca 1 Weather Forecast** is an Enigma2 plugin that provides detailed weather forecasts for up to 10 days, using public data from the Foreca website. It includes features such as:

- Current weather with extended details (feels-like temperature, dew point, wind, gusts, humidity, pressure, UV, AQI, rain/snow probability, update time).
- Hourly forecast for the selected day.
- 7-day daily forecast with min/max temperatures, wind, precipitation, and description.
- Meteogram with temperature curves, rain bars, hourly icons, and wind.
- Nearby observation stations (via scraping or authenticated API).
- Weather maps: Wetterkontor (slideshow) and, if configured, Foreca 1 live maps (require credentials).
- Moon phases with rise/set times and Earth-Moon distance.
- Multilingual support (integrated translations).
- Customizable colors and transparency.
- Choice between metric and imperial systems, with the ability to customize individual units (wind, pressure, temperature, precipitation).

---

## Installation
1. Copy the `Foreca1` folder to the Enigma2 plugins directory:  
   `/usr/lib/enigma2/python/Plugins/Extensions/`
2. Ensure correct permissions (755 for folders, 644 for files).
3. Restart Enigma2 or the plugin menu to make the plugin visible.

---

## Initial Configuration

### Offline City List
The plugin uses a `new_city.cfg` file containing the list of supported cities. If the file does not exist, online search will be used (see below). You can generate it manually (format: `ID/City_Name` per line) or let the plugin create it automatically during online search.

### API Credentials (Optional)
Some advanced features (Foreca1 live maps, observation stations via API) require a Foreca account and valid credentials.  
To configure them:
1. Create an `api_config.txt` file in the plugin folder (`/usr/lib/enigma2/python/Plugins/Extensions/Foreca1/api_config.txt`).
2. Insert the following lines (replace with your data):
   ```
   API_USER=your_username
   API_PASSWORD=your_password
   ```
3. Optionally, you can modify other parameters such as the map server or token duration (see the example file `api_config.txt.example`).

Without these credentials, live maps and API stations will not work; a fallback to scraping will be attempted where possible.

---

## Using the Plugin

### Main Screen
Upon launching the plugin, the main screen displays:
- Selected city, date, and day name.
- Current weather: icon, temperature, description.
- Details: feels-like temperature, dew point, wind (speed and direction), gusts, rain, humidity, pressure, UV, AQI, rain/snow probability, update time.
- Sun information: sunrise, sunset, day length.
- Moon phase: icon, phase name, illumination, distance, rise and set times.
- Nearest observation station (if available).
- Hourly list for the selected day (scrollable with UP/DOWN keys).

**Function keys:**
- **0-9**: directly jump to the corresponding day (0 = today, 1 = tomorrow, ... 9 = today+9).
- **LEFT/RIGHT ARROW**: previous/next day.
- **OK**: opens the today/tomorrow detail screen (with periods and radar map).
- **RED**: opens the color selector.
- **GREEN**: loads favorite 1 (city saved in `fav1.cfg`).
- **YELLOW**: loads favorite 2 (`fav2.cfg`).
- **BLUE**: loads the home city (`home.cfg`).
- **MENU**: opens the main menu.
- **INFO**: opens the plugin information window.
- **EXIT**: exits the plugin (returns to TV or plugin menu).

### Main Menu
Pressing **MENU** opens a choice with the following options:

- **City Selection**: opens the city search panel.
- **Weather Maps**: submenu to choose between Wetterkontor maps (slideshow) and Foreca1 live maps (if configured).
- **Weekly Forecast**: opens the 7-day detailed forecast screen.
- **Meteogram**: displays the 7-day meteogram.
- **Station Observations**: shows nearby weather stations.
- **Unit Settings (Simple)**: quick choice between metric and imperial systems.
- **Unit Settings (Advanced)**: allows customization of individual units (wind, pressure, temperature, precipitation).
- **Color Selector**: changes the background color of the plugin.
- **Transparency**: adjusts the transparency of overlays.
- **Info**: plugin information and credits.
- **Exit**: closes the plugin.

### City Selection
The `City Selection` screen allows you to search for a city:
- **RED**: opens the virtual keyboard to enter the city name.
- The search is performed first online (via Foreca API) and, if no results are found, an offline search on the `new_city.cfg` file is performed.
- **GREEN**: assigns the selected city to favorite 1.
- **YELLOW**: assigns to favorite 2.
- **BLUE**: assigns to home.
- **OK**: loads the selected city into the main screen and closes the panel.
- **EXIT**: returns to the menu without changes.

### Daily Forecast (7 days)
Displays a list of the next 7 days. Each row contains:
- Abbreviated day name and date.
- Min/max temperatures (converted according to chosen units).
- Abbreviated weather description.
- Precipitation probability.
- Wind speed and direction.

**Navigation:**
- **UP/DOWN**: move selection.
- **PAGE UP/PAGE DOWN**: jump one page.
- **OK**: opens a window with complete details of the selected day.
- **EXIT**: returns to the main menu.

### Meteogram
Graphical screen showing temperature trends (with colored curve), precipitation bars, weather icons, and wind direction for each 3-hour interval over the next 7 days. It also includes temperature and precipitation scales and date markers.

**Keys:**
- **OK/EXIT**: close the meteogram.

### Observation Stations
Displays a list of weather stations near the selected location. Data comes from:
1. Authenticated API (if configured and available).
2. Fallback: scraping of the Foreca website.

For each station, the following are displayed:
- Name, distance (if available), temperature, feels-like temperature, dew point, humidity, pressure, visibility, update time.
- **UP/DOWN**: navigate through stations.
- **OK**: updates details (if not already visible).

### Weather Maps
The **Weather Maps** submenu offers two options:

#### Wetterkontor Maps (slideshow)
Displays a series of maps (6 images) for the selected region (Europe, Germany, continents).  
- **RED**: play/pause slideshow.
- **GREEN**: next image.
- **YELLOW**: previous image.
- **BLUE**: exit.
- **UP/DOWN**: increase/decrease slideshow speed.

#### Foreca 1 Live Maps (API)
Requires valid credentials. If configured, it shows a list of available layers (temperature, wind, clouds, etc.). After selection, the viewer opens with:
- **LEFT/RIGHT ARROW**: change time (if multiple times available).
- **GREEN**: zoom in.
- **YELLOW**: zoom out.
- **RED/EXIT**: close.

Note: without credentials, this option will not be available.

### Unit Settings
Two modes:

**Simple**: allows choosing between metric (Celsius, km/h, hPa, mm) and imperial (Fahrenheit, mph, inHg, in) systems. Selection is done with UP/DOWN keys and confirmed with GREEN.

**Advanced**: allows customization of each category:
- Wind: km/h, m/s, mph, kts.
- Pressure: hPa, mmHg, inHg.
- Temperature: °C, °F.
- Precipitation: mm, in.

Navigation between categories is done with YELLOW (next) and BLUE (prev). Within a category, select the unit with OK (a checkmark appears). Finally, press GREEN to save all settings.

After saving, the main screen updates immediately with the new units.

### Color and Transparency
- **Color Selector**: lists a series of predefined colors (from the `color_database.txt` file). Use UP/DOWN to move, OK to confirm. The color is applied immediately to all screens (global theme).
- **Transparency**: lists different transparency levels (from 6% to 56%). OK confirms, and the change is visible immediately.

### Plugin Info
Shows the version, authors, and credits. Press OK or EXIT to close.

---

## Authenticated API Configuration (Optional)

To use Foreca 1 live maps and observation stations via API, you need a valid Foreca account. Follow these steps:

1. Obtain username and password from the Foreca service (not provided by the plugin).
2. Create the file `api_config.txt` in the plugin folder with the following content:
   ```
   API_USER=your_username
   API_PASSWORD=your_password
   ```
3. (Optional) Modify other parameters such as:
   - `TOKEN_EXPIRE_HOURS` (default 720) – access token duration.
   - `MAP_SERVER` (default map-eu.foreca.com) – map server.
   - `AUTH_SERVER` (default pfa.foreca.com) – authentication server.

An example file (`api_config.txt.example`) is created automatically if the main file does not exist.

**Note**: without these credentials, menu items related to live maps may not appear or may show an error. The plugin still works perfectly for all other features.

---

## Troubleshooting

### 1. The main screen does not show weather data
- Check internet connection.
- Verify that the selected city is valid (try with another city).
- Look at debug files in the plugin's `debug/` folder for possible errors.

### 2. City search finds no results
- Online search might be temporarily unavailable. Check if `api.foreca.net` is reachable.
- Ensure the `new_city.cfg` file exists and contains at least a few cities (if you prefer offline mode).
- Try searching with a more generic term (e.g., "Rome" instead of "Rome, Italy").

### 3. Live maps do not work
- Check that the `api_config.txt` file exists and contains correct credentials.
- Verify that your Foreca account has access to map APIs (some accounts may be limited).
- Enable debug (`DEBUG = True` in `plugin.py`) and check logs for authentication errors.

### 4. Navigation in DailyForecast does not respond
- Make sure you are pressing UP/DOWN keys, not numeric keys (which change the day in the main screen). In the weekly forecast screen, numeric keys have no effect.
- Verify that the skin has a `list` widget with adequate dimensions.

### 5. Units do not update after saving
- This issue has been fixed in recent versions. If it persists, check that the `units_closed` callback is present in `plugin.py` and that the unit screens return `True` upon saving.

### 6. Color is not applied to all screens
- The function `apply_global_theme` must be called in every secondary screen (already done for all main screens). If some custom screen lacks the `background_plate` and `selection_overlay` widgets, the theme will not be applied.

---

## Credits
- **Original project idea by**: @Bauernbub
- **Modifications and subsequent developments**: @Lululla
- **Contributions**: Assistant (API refactoring, meteogram implementation, new data integration, extensive debugging, menu navigation, station scraping, lunar data integration, advanced units, global color, DailyForecast fixes)

Thank you for choosing Foreca 1 Weather Forecast! For suggestions or reports, visit the reference forums (LinuxSatSupport, Corvoboys).