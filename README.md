# 🌤️ Foreca Weather Forecast for Enigma2

<p align="center">
  <img src="https://github.com/Belfagor2005/ForecaOne/blob/main/usr/lib/enigma2/python/Plugins/Extensions/Foreca1/buttons/ForecaOne.png" alt="Foreca One by Lululla" width="250">
</p>

<p align="center">
  <a href="https://github.com/Belfagor2005/ForecaOne">
    <img src="https://img.shields.io/badge/Version-1.0.1-blue.svg" alt="Version">
  </a>
  <a href="https://www.gnu.org/licenses/gpl-3.0.html">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.x-yellow.svg" alt="Python">
  </a>
</p>

---

## 🌍 Overview

**Foreca1 Weather Forecast** is a comprehensive Enigma2 plugin that provides accurate and detailed weather forecasts for up to 10 days using data from **Foreca**. It offers both free public data and authenticated API access for enhanced features like live weather maps.

Whether you are a casual user or a weather enthusiast, this plugin delivers all the information you need right on your Enigma2 receiver.

---

## ✨ Key Features

### ✅ Works with or without API
- **Free mode** – uses public Foreca endpoints and scraping for most features.
- **API mode** – unlock live maps, station observations, and more with a free 30-day trial.

### 📊 Weather Data
- **Current conditions** with extended details:
  - Temperature, feels like, dew point
  - Wind speed, gusts, direction
  - Humidity, pressure, UV index, AQI
  - Rain/snow probability and amount
  - Last update time
- **10‑day daily forecast** (min/max temp, wind, precipitation, weather symbol)
- **Hourly forecast** for the selected day (scrolling list with icons)
- **7‑day meteogram** – temperature curve, rain bars, wind info

### 🌙 Moon Information
- Moon phase with icon
- Illumination percentage
- Earth–Moon distance
- Moonrise and moonset times (from USNO API, async)

### 📡 Observation Stations
- Nearby weather stations (from authenticated API or scraping)
- Temperature, feels like, humidity, pressure, wind, visibility

### 🗺️ Weather Maps
- **Wetterkontor slideshow** – regional maps (Europe, Germany, continents)
- **Foreca1 Live Maps (API)** – temperature, wind, precipitation, clouds, radar
  - 3×3 tile grid with zoom in/out
  - Timeline support (change forecast time)
  - Background overlays for geography
  - Local tile cache to save API quota

### ⚙️ Advanced Unit Management
- Choose between **Metric** and **Imperial** systems
- **Customizable units**:
  - Wind: km/h, m/s, mph, kts
  - Pressure: hPa, mmHg, inHg
  - Temperature: °C, °F
  - Precipitation: mm, in
- Changes apply instantly – no restart needed

### 🎨 User Interface
- **Global color theme** – set once, applied to all screens
- **Transparency** – adjustable overlay transparency
- **Multilingual** – full GetText support with Google Translate fallback
- **Keyboard navigation** – all screens are fully controllable via remote

### 🔧 Technical Highlights
- Python 3 compatible
- Asynchronous downloads (moon data, maps, stations)
- Debug mode with detailed logs
- Smart caching (tiles, API tokens, translations)
- Skin system with FHD, HD, WQHD support

---

## 📅 Project Information

- **First release:** 01/03/2026
- **Source of weather data:** [https://www.foreca.com](https://www.foreca.com)
- **License:** GNU General Public License v3.0

---

## 🚀 Installation

1. Copy the `Foreca1` folder to your Enigma2 plugins directory:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/
   ```
2. Set correct permissions:
   ```
   chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Foreca1
   ```
3. Restart Enigma2 or the plugin menu.

---

## 🔑 API Configuration (Optional)

To enable live maps and authenticated station data, you need a **free Foreca trial account**:

1. Register at [https://developer.foreca.com](https://developer.foreca.com) (30‑day trial, 1000 tile requests/day).
2. Create a file `api_config.txt` in the plugin folder:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/Foreca1/api_config.txt
   ```
3. Add your credentials:
   ```ini
   API_USER=your_username
   API_PASSWORD=your_password
   TOKEN_EXPIRE_HOURS=720
   MAP_SERVER=map-eu.foreca.com
   AUTH_SERVER=pfa.foreca.com
   ```
4. An example file `api_config.txt.example` is provided.

> **Without API credentials** the plugin still works perfectly using public data and scraping.

---

## 🧭 How to Use

### Main Screen
- **0‑9** – jump to day (0 = today)
- **LEFT/RIGHT** – previous/next day
- **OK** – open today/tomorrow detail + radar map
- **RED** – color selector
- **GREEN** – load favorite 1
- **YELLOW** – load favorite 2
- **BLUE** – load home city
- **MENU** – open main menu
- **INFO** – about plugin
- **EXIT** – close plugin

### Main Menu
- **City Selection** – search and assign favorites
- **Weather Maps** – Wetterkontor slideshow or Foreca1 live maps
- **Weekly Forecast** – 7‑day detailed forecast
- **Meteogram** – graphical 7‑day trend
- **Station Observations** – nearby stations
- **Unit Settings** – simple (metric/imperial) or advanced (custom units)
- **Color Selector** – change global background color
- **Transparency** – adjust overlay transparency
- **Info** – version and credits

---

## 🌐 Language Support

The plugin uses **GetText** for translations. Currently supported languages:

- English (en)
- Italian (it)
- German (de)
- French (fr)
- Spanish (es)
- … and many more (fallback to English)

If your language is missing, you can contribute by translating the `.po` files.

---

## 🗺️ Foreca1 Live Maps – Details

### How it works
1. **Capabilities request** – fetches available layers from Foreca1.
2. **Tile grid** – downloads a 3×3 grid of tiles (size depends on screen resolution).
3. **Background overlay** – each layer is overlaid on a geographic background (e.g. `europa.png`, `temp_map.png`).
4. **Timeline** – use LEFT/RIGHT to browse forecast times.
5. **Zoom** – zoom in/out with GREEN/YELLOW.

### Background mapping

| Layer type       | Background PNG       |
|------------------|----------------------|
| Temperature      | `temp_map.png`       |
| Precipitation    | `rain_map.png`       |
| Wind             | `europa.png`         |
| Clouds           | `cloud_map.png`      |
| Pressure         | `pressure_map.png`   |
| Radar            | `rain_map.png`       |

Regional backgrounds (e.g. `italien.png`, `deutschland.png`) are used when available.

---

## 📦 Version History

### 1.0.0 (01/03/2026)
- Complete rewrite from original code by @Bauernbub
- Added authenticated map API support
- Implemented global color theme and transparency
- Introduced advanced unit management
- Full translation system with GetText
- Asynchronous moon data
- Many bug fixes and optimizations
- Thanks to @Orlandox and all testers!

---

## 👥 Credits

- **Original design & idea:** @Bauernbub
- **Major recode & maintenance:** @Lululla
- **Contributions:** Assistant (API refactoring, meteogram, translations, unit system, map viewer, and many fixes)

---

## ⚠️ Known Limitations & Future Work

- **Satellite imagery** – API supports it, not yet implemented in viewer.
- **Wind background** – no dedicated wind map, falls back to `europa.png`.
- **Trial plan limit** – 1000 tile requests per day; the cache helps, but heavy usage may exceed it.
- **Map panning** – currently not implemented (only zoom and time change).

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Enjoy the weather, rain or shine! ☀️🌧️</i><br>
  © Lululla 2026
</p>
