#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Foreca One Weather Forecast for Enigma2
# Copyright (C) 2026 @Lululla
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# -------------------------------------------------------
#
#          Foreca One Weather Forecast E2
#
#   This Plugin retrieves the actual weather forecast
#   for the next 10 days from the Foreca website.
#        We wish all users wonderful weather!
#
#     Source of information: https://www.foreca.com
#     Original design and idea by @Bauernbub
#     Enigma2 all code rewrite by @Lululla, 2026
#     Thank's @Orlandox and other friends for suggestions and test
# -------------------------------------------------------

from __future__ import absolute_import

import datetime
from os import chmod, makedirs
from os.path import exists, join
from threading import Thread

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Timezones import Timezones


from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox

from enigma import gRGB, eTimer
from skin import parseColor

from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap

from . import (
    _,
    VERSION,
    INSTALLER_URL,
    PLUGIN_PATH,
    MOON_ICON_PATH,
    load_skin_for_class,
    DEBUG,
    TEMP_DIR,
    DBG_DIR,
    CONFIG_FILE,
    SYSTEM_DIR
)

from .city_panel import CityPanel4
from .color_selector import ColorSelector
from .daily_forecast import DailyForecast
from .foreca_map_api import ForecaMapAPI
from .foreca_map_menu import ForecaMapMenu
from .foreca_stations import ForecaStations
from .favorites_detail import FavoritesDetailView
from .foreca_weather_api import (
    ForecaWeatherAPI,
    ForecaFreeAPI,
    _symbol_to_description,
)
from .google_translate import (
    _get_system_language,
    translate_batch_strings,
    trans
)
from .info_dialog import InfoDialog
from .meteogram import MeteogramView
from .moon_calendar import MoonCalendar
from .slideshow import ForecaMapsMenu
from .transparency_selector import TransparencySelector
from .unit_manager import UnitManager, UnitSettingsSimple
from .weather_detail import WeatherDetailView
from .MoonPhase import MoonPhase
from .hour_detail import HourDetailView


# ---------- Utility functions ----------
TARGET_LANG = _get_system_language()


def is_valid(v):
    """Return True if value is not None and not a string representing 'N/A'."""
    if v is None:
        return False
    s = str(v).strip().lower()
    return s not in ('', 'n/a', 'none', 'null')


def conv_day_len(indata):
    return indata


def my_speed_wind(indata, metka):
    try:
        val = float(indata)
        if metka == 1:
            return '%.01f' % val
        else:
            return '%.01f' % val
    except BaseException:
        return '0.00'


def cleanup_temp_files():
    """Removes the temporary folder and all SVG files inside it."""
    import shutil
    if exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            if DEBUG:
                print(f"[Meteogram] Cleaned folder {TEMP_DIR}")
        except Exception as e:
            print(f"[Meteogram] Error cleaning {TEMP_DIR}: {e}")

    if exists(DBG_DIR):
        try:
            shutil.rmtree(DBG_DIR)
            if DEBUG:
                print(f"[Meteogram] Cleaned folder {DBG_DIR}")
        except Exception as e:
            print(f"[Meteogram] Error cleaning {DBG_DIR}: {e}")


def _write_favorite_debug(text):
    """Write debug info to favorite_debug.txt in the plugin's debug folder."""
    try:
        dbg_path = join(DBG_DIR, "favorite_debug.txt")
        with open(dbg_path, "a", encoding="utf-8") as dbg:
            dbg.write(text + "\n")
    except Exception as e:
        print(f"[Favorite Debug] Error writing debug file: {e}")


def write_forecast_weather_debug(text):
    try:
        dbg_path = join(DBG_DIR, "forecast_weather_debug.txt")
        with open(dbg_path, "a") as dbg:
            dbg.write(text + "\n")
    except Exception as e:
        print(f"[Foreca1] Forecast debug write error: {e}")


def write_current_weather_debug(text):
    try:
        dbg_path = join(DBG_DIR, "current_weather_debug.txt")
        with open(dbg_path, "a") as dbg:
            dbg.write(text + "\n")
    except Exception as e:
        print(f"[Foreca1] Current debug write error: {e}")


def write_meteogram_debug(text):
    try:
        dbg_path = join(DBG_DIR, "meteogram_debug.txt")
        with open(dbg_path, "a") as dbg:
            dbg.write(text + "\n")
    except Exception as e:
        print(f"[Meteogram] Debug write error: {e}")


# ---------- End Debug ----------


class Foreca_Preview(Screen, HelpableScreen):

    def __init__(self, session):
        self.session = session

        self.unit_manager = UnitManager(PLUGIN_PATH)
        self.weather_api = ForecaFreeAPI(self.unit_manager)
        # Initialize authenticated API (for stations and maps)
        self.weather_api_auth = None
        try:
            self.weather_api_auth = ForecaWeatherAPI(self.unit_manager)
            if not self.weather_api_auth.check_credentials():
                self.weather_api_auth = None
                if DEBUG:
                    print(
                        "[Foreca1] Authenticated API not configured (no credentials)")
        except Exception as e:
            print(f"[Foreca1] Authenticated API initialization error: {e}")
            self.weather_api_auth = None

        # Initialize all attributes
        self.town = 'N/A'
        self.cur_temp = 'N/A'
        self.fl_temp = 'N/A'
        self.dewpoint = 'N/A'
        self.pic = 'N/A'
        self.wind = 'N/A'
        self.wind_speed = 'N/A'
        self.wind_gust = 'N/A'
        self.rain_mm = 'N/A'
        self.hum = 'N/A'
        self.pressure = 'N/A'
        self.country = 'N/A'
        self.lon = 'N/A'
        self.lat = 'N/A'
        self.sunrise = 'N/A'
        self.daylen = 'N/A'
        self.sunset = 'N/A'
        self.f_town = 'N/A'

        self.uvi = 'N/A'
        self.aqi = 'N/A'
        self.rainp = 'N/A'
        self.snowp = 'N/A'
        self.updated = 'N/A'

        self.f_date = []
        self.f_time = []
        self.f_symb = []
        self.f_cur_temp = []
        self.f_flike_temp = []
        self.f_wind = []
        self.f_wind_speed = []
        self.f_precipitation = []
        self.f_rel_hum = []
        self.f_day = 'N/A'
        self.myloc = 0
        self.tag = 0

        # Load colors and transparency from file (if they exist)
        self.rgbmyr, self.rgbmyg, self.rgbmyb = self._read_color()
        self.alpha = self._read_alpha()

        # Read Favorites
        self.path_loc0 = self._read_favorite('home') or '103169070/Rome-Italy'
        self.path_loc1 = self._read_favorite(
            'fav1') or '100524901/Moscow-Russia'
        self.path_loc2 = self._read_favorite(
            'fav2') or '102961214/Thurles-County-Tipperary-Ireland'
        self.skin = load_skin_for_class(Foreca_Preview)

        Screen.__init__(self, session)

        HelpableScreen.__init__(self)
        self.setTitle(
            _("Foreca One Weather Forecast") +
            " " +
            _("v.") +
            VERSION)

        self.timezones = Timezones()
        self.tz = None

        # ========== TITLE WIDGETS ==========
        self["title_main"] = StaticText()
        self["title_version"] = StaticText()
        self["maintener"] = StaticText()
        self["title_loading"] = StaticText(_("Please wait ..."))
        self["title_sub"] = StaticText()
        self["title_section"] = StaticText()
        self["title_section_weather"] = StaticText()
        self["current_time"] = Label("")

        self.time_timer = eTimer()
        self.time_timer.callback.append(self.update_time)
        self.time_timer.start(1000)

        # ========== BACKGROUND AND OVERLAY ELEMENTS (for theming) ==========
        self["selection_overlay"] = Label("")
        self["background_plate"] = Label("")
        self["color_bg_today"] = Label("")
        self["color_bg_forecast"] = Label("")
        self["color_bg_sun"] = Label("")
        self["color_bg_coords"] = Label("")
        self["transp_bg_today"] = Label("")
        self["transp_bg_forecast"] = Label("")
        self["transp_bg_sun"] = Label("")
        self["transp_bg_coords"] = Label("")
        self["transp_bg_header"] = Label("")

        self["key_green"] = StaticText(_("Favorite 1"))
        self["key_yellow"] = StaticText(_("Favorite 2"))
        self["key_blue"] = StaticText(_("Home"))
        self["key_red"] = StaticText(_("Color"))
        self["key_menu"] = StaticText(_("Menu"))
        self["key_info"] = StaticText(_("Info"))
        self["key_help"] = StaticText(_("Help"))
        self["key_ok"] = StaticText(_("Ok - Zone"))

        # ========== CURRENT WEATHER MAIN INFO ==========
        self["weather_description"] = Label('')
        self["icon_weather"] = Pixmap()

        # ========== OBSERVATION STATION ==========
        self["icon_observation"] = Pixmap()
        self["station_name"] = Label("N/A")

        # ========== LOCATION AND TEMPERATURE ==========
        self["city_name"] = Label("N/A")
        self["temperature_current"] = Label("N/A")

        # ========== FEELS LIKE TEMPERATURE ==========
        self["icon_temp_perc"] = Pixmap()
        self["temperature_feelslike"] = Label("N/A")

        # ========== DEW POINT ==========
        self["icon_dew_point"] = Pixmap()
        self["dewpoint_value"] = Label("N/A")

        # ========== WIND SPEED AND DIRECTION ==========
        self["icon_wind_speed"] = Pixmap()
        self["icon_wind"] = Pixmap()
        self["icon_wind_direction"] = Pixmap()
        self["wind_speed_value"] = Label("N/A")

        # ========== WIND GUST ==========
        self["wind_gust_value"] = Label("N/A")
        self["icon_wind_burst"] = Pixmap()

        # ========== RAIN AND HUMIDITY ==========
        self["rain_value"] = Label("N/A")
        self["humidity_value"] = Label("N/A")

        # ========== PRESSURE ==========
        self["barometer_desc"] = Label(_("Barometer"))
        self["pressure_value"] = Label("N/A")
        self["icon_pressure"] = Pixmap()

        # ========== STATIC ICONS (rain, humidity) ==========
        self["icon_rain"] = Pixmap()
        self["icon_humidity"] = Pixmap()

        # ========== UV INDEX ==========
        self["uvi_value"] = Label("N/A")
        self["icon_uvi"] = Pixmap()
        self["uvi_desc"] = Label("")

        # ========== AIR QUALITY INDEX (AQI) ==========
        self["icon_aqi"] = Pixmap()
        self["aqi_value"] = Label("N/A")

        # ========== RAIN PROBABILITY ==========
        self["icon_rainp"] = Pixmap()
        self["rainp_value"] = Label("N/A")

        # ========== SNOW PROBABILITY ==========
        self["icon_snowp"] = Pixmap()
        self["snowp_value"] = Label("N/A")

        # ========== LAST UPDATE TIME ==========
        self["icon_updated"] = Pixmap()
        self["updated_label"] = Label("N/A")

        # ========== SUN INFO ==========
        self["icon_sun"] = Pixmap()
        self["day_length"] = Label('0 h 0 min')
        self["sunrise_label"] = Label(_('Sunrise'))
        self["icon_sunrise"] = Pixmap()
        self["sunrise_value"] = Label('00:00')
        self["sunset_label"] = Label(_('Sunset'))
        self["icon_sunset"] = Pixmap()
        self["sunset_value"] = Label('00:00')

        # Initialize the lunar phase handler
        # Add moon widgets (if they are not already in the skin)
        self.moon = MoonPhase(icon_path=MOON_ICON_PATH, total_icons=32)
        self["icon_moon"] = Pixmap()
        self["moon_label"] = Label()
        self["icon_moon_light"] = Pixmap()
        self["moon_illum"] = Label()
        self["icon_moon_dist"] = Pixmap()
        self["moon_distance"] = Label()
        self["moonrise_label"] = Label(_("Rise"))
        self["icon_moonrise"] = Pixmap()
        self["moonrise_value"] = Label()
        self["moonset_label"] = Label(_("Sets"))
        self["icon_moonset"] = Pixmap()
        self["moonset_value"] = Label()

        self.list = []
        self["menu"] = List(self.list)

        self.color = gRGB(255, 255, 255)
        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.exit, _("Exit - End")),
                "showEventInfo": (self.info, _("Info - About")),
                "menu": (self.Menu, _("Menu - Settings")),
                "left": (self.left, _("Left - Previous day")),
                "right": (self.right, _("Right - Next day")),
                "up": (self.up, _("Up - Previous page")),
                "ok": (self.OK, _("OK - Ext Info")),
                "down": (self.down, _("Down - Next page")),
                "previous": (self.previousDay, _("Left arrow - Previous day")),
                "next": (self.nextDay, _("Right arrow - Next day")),
                "nextBouquet": (self.nextUp, _("Page Up")),
                "prevBouquet": (self.nextDown, _("Page Down")),
                "red": (self.red, _("Red - Color select")),
                "green": (self.Fav1, _("Green - Favorite 1")),
                "yellow": (self.Fav2, _("Yellow - Favorite 2")),
                "blue": (self.Fav0, _("Blue - Home")),
                "0": (boundFunction(self.keyNumberGlobal, 0), _("0 - Today")),
                "1": (boundFunction(self.keyNumberGlobal, 1), _("1 - Today + 1 day")),
                "2": (boundFunction(self.keyNumberGlobal, 2), _("2 - Today + 2 days")),
                "3": (boundFunction(self.keyNumberGlobal, 3), _("3 - Today + 3 days")),
                "4": (boundFunction(self.keyNumberGlobal, 4), _("4 - Today + 4 days")),
                "5": (boundFunction(self.keyNumberGlobal, 5), _("5 - Today + 5 days")),
                "6": (boundFunction(self.keyNumberGlobal, 6), _("6 - Today + 6 days")),
                "7": (boundFunction(self.keyNumberGlobal, 7), _("7 - Today + 7 days")),
                "8": (boundFunction(self.keyNumberGlobal, 8), _("8 - Today + 8 days")),
                "9": (boundFunction(self.keyNumberGlobal, 9), _("9 - Today + 9 days")),
            },
            -1
        )
        if DEBUG:
            print("[DEBUG] Action map creata")
        self.onLayoutFinish.append(self.StartPageFirst)
        self.onLayoutFinish.append(self._update_moon)
        self.onShow.append(self._update_button)

    def StartPageFirst(self):
        """Initialize page with fallback icons and load favorite 0."""
        self._load_favorite(0, self.path_loc0)

        # ---- WEATHER ICON (fallback) ----
        fallback_weather = join(PLUGIN_PATH, "thumb", "d000.png")
        if exists(fallback_weather):
            self["icon_weather"].instance.setPixmapFromFile(fallback_weather)
            self["icon_weather"].instance.show()

        # ---- WIND ICON (fallback) ----
        fallback_wind = join(PLUGIN_PATH, "thumb", "wS.png")
        if exists(fallback_wind):
            self["icon_wind"].instance.setPixmapFromFile(fallback_wind)
            self["icon_wind"].instance.show()

        # ---- STATIC ICONS ----
        static_icons = {
            "icon_aqi": "aqi.png",
            "icon_wind_direction": "wind_direction.png",
            "icon_wind_burst": "wind_burst.png",
            "icon_dew_point": "dew_point.png",
            "icon_humidity": "humidity.png",
            "icon_observation": "observation.png",
            "icon_pressure": "barometer.png",
            "icon_rain": "precipitation.png",
            "icon_rainp": "rain_prob.png",
            "icon_snowp": "snow_prob.png",
            "icon_sun": "day_light.png",
            "icon_temp_perc": "temp_perc.png",
            "icon_updated": "updated.png",
            "icon_uvi": "uva.png",
            "icon_wind_speed": "wind_speed.png",
        }
        for widget, filename in static_icons.items():
            path = join(PLUGIN_PATH, "images", filename)
            if exists(path):
                self[widget].instance.setPixmapFromFile(path)
                self[widget].instance.show()
            else:
                if DEBUG:
                    print(f"[Foreca1] Missing static icon: {path}")

        # ---- START THREAD TO LOAD MAP ----
        if self.lat != 'N/A' and self.lon != 'N/A':
            Thread(target=self.mypicload).start()

    def mypicload(self):
        """Download radar map."""
        if not is_valid(self.lon) or not is_valid(self.lat):
            return
        import subprocess
        base_url = "https://map-cf.foreca.net/teaser/map/light/rain/6/"
        output_file = join(TEMP_DIR, '385.png')
        full_url = f"{base_url}{self.lon}/{self.lat}/317/385.png?names"
        cmd = ['wget', '-O', output_file, full_url]
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if exists(output_file):
                # if there is a radar_map widget, update it
                pass
        except Exception as e:
            print("[Foreca1] Map download error:", e)

    def OK(self):
        menu = [
            (_("Selected hour details"), "hour"),
            (_("Today/Tomorrow details"), "day"),
            (_("Favorites details"), "favorites")
        ]
        self.session.openWithCallback(
            self.okChoiceCallback,
            ChoiceBox,
            title=_("Choose detail view"),
            list=menu
        )

    def okChoiceCallback(self, choice):
        if choice is None:
            return
        action = choice[1]
        if action == "hour":
            idx = self["menu"].getIndex()
            if idx is not None and 0 <= idx < len(self.f_time):
                hour_data = {
                    "time": self.f_time[idx],
                    "temp": self.f_cur_temp[idx],
                    "feels_like": self.f_flike_temp[idx],
                    "condition": self.f_symb[idx],
                    "wind_dir": self.f_wind[idx],
                    "wind_speed": self.f_wind_speed[idx],
                    "precipitation": self.f_precipitation[idx],
                    "humidity": self.f_rel_hum[idx],
                    "uvi": self.f_uvi[idx] if hasattr(
                        self,
                        'f_uvi') and idx < len(
                        self.f_uvi) else 'N/A',
                    "date": self.f_date[0] if self.f_date else "N/A",
                    "day": self.f_day if self.f_day else "N/A",
                    "town": self.town,
                    "country": self.country,
                }
                self.session.open(
                    HourDetailView,
                    self.weather_api,
                    self,
                    self.unit_manager,
                    hour_data)
        elif action == "day":
            self.session.open(
                WeatherDetailView,
                self.weather_api,
                self,
                self.unit_manager)
        elif action == "favorites":
            self.session.open(
                FavoritesDetailView,
                self.weather_api,
                self,
                self.unit_manager)
        else:
            return

    def keyNumberGlobal(self, number):
        self.tag = number
        self._load_favorite(
            self.myloc, [self.path_loc0, self.path_loc1, self.path_loc2][self.myloc])

    def red(self):
        self.session.open(ColorSelector, self)

    def left(self):
        if self.tag > 0:
            self.tag -= 1
            self._load_favorite(
                self.myloc, [self.path_loc0, self.path_loc1, self.path_loc2][self.myloc])

    def right(self):
        if self.tag < 9:
            self.tag += 1
            self._load_favorite(
                self.myloc, [self.path_loc0, self.path_loc1, self.path_loc2][self.myloc])

    def nextUp(self):
        self["menu"].pageUp()

    def nextDown(self):
        self["menu"].pageDown()

    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    def previousDay(self):
        self.left()

    def nextDay(self):
        self.right()

    def info(self):
        self.session.open(InfoDialog, self)

    def Menu(self):
        menu_items = [
            (_("City Selection"), "city"),
            (_("Weather Maps"), "maps"),
            (_("Weekly Forecast"), "daily_forecast"),
            (_("Meteogram"), "meteogram"),
            (_("Station Observations"), "stations"),
            (_("Unit Settings (Simple)"), "units_simple"),
            (_("Unit Settings (Advanced)"), "units_advanced"),
            (_("Lunar Calendar"), "moon_calendar"),
            (_("Color select"), "colorselector"),
            (_("Transparency Settings"), "transparency"),
            (_("Check for updates"), "update"),
            (_("Info"), "info"),
            (_("Exit"), "exit")
        ]
        self.menu_dialog = self.session.openWithCallback(
            self.menu_callback,
            ChoiceBox,
            title=_("Foreca One Menu"),
            list=menu_items
        )

    def menu_callback(self, choice):
        if choice is None:
            return
        key = choice[1]
        if key == "city":
            self.session.openWithCallback(
                self.city_selected, CityPanel4, self.menu_dialog)
        elif key == "daily_forecast":
            location_id = [self.path_loc0, self.path_loc1,
                           self.path_loc2][self.myloc].split('/')[0]
            location_name = self.town
            if location_id:
                self.session.openWithCallback(
                    self.after_main_menu,
                    DailyForecast,
                    self.weather_api,
                    location_id,
                    location_name)
            else:
                self.session.open(
                    MessageBox,
                    _("No location selected"),
                    MessageBox.TYPE_INFO)
        elif key == "meteogram":
            location_id = [self.path_loc0, self.path_loc1,
                           self.path_loc2][self.myloc].split('/')[0]
            location_name = self.town
            if location_id:
                self.session.openWithCallback(
                    self.after_main_menu,
                    MeteogramView,
                    self.weather_api,
                    location_id,
                    location_name,
                    self.unit_manager)
            else:
                self.session.open(
                    MessageBox,
                    _("No location selected"),
                    MessageBox.TYPE_INFO)
        elif key == "stations":
            location_id = [self.path_loc0, self.path_loc1,
                           self.path_loc2][self.myloc].split('/')[0]
            location_name = self.town
            if location_id:
                self.session.openWithCallback(
                    self.after_main_menu,
                    ForecaStations,
                    self.weather_api,
                    getattr(self, 'weather_api_auth', None),
                    location_id,
                    location_name,
                    self.unit_manager,
                    getattr(self, 'tz', None),
                    getattr(self, 'tz_offset', None)
                )
            else:
                self.session.open(
                    MessageBox,
                    _("No location selected"),
                    MessageBox.TYPE_INFO)
        elif key == "units_simple":
            self.session.openWithCallback(
                self.after_units, UnitSettingsSimple, self.unit_manager)
        elif key == "units_advanced":
            from .unit_manager import UnitSettingsAdvanced
            self.session.openWithCallback(
                self.after_units,
                UnitSettingsAdvanced,
                self.unit_manager)
        elif key == "moon_calendar":
            self.session.openWithCallback(
                self.after_main_menu, MoonCalendar, self.moon)
        elif key == "colorselector":
            self.session.openWithCallback(
                self.after_main_menu, ColorSelector, self)
        elif key == "transparency":
            self.session.openWithCallback(
                self.after_main_menu, TransparencySelector, self)
        elif key == "update":
            self.update_me()
        elif key == "maps":
            self.open_maps_menu()
        elif key == "info":
            self.session.openWithCallback(
                self.after_main_menu, InfoDialog, self)
        elif key == "exit":
            return

    def city_selected(self, result):
        if result is None:
            return

        if isinstance(result, tuple) and len(result) >= 2:
            city_id, action = result[0], result[1]
            if action == 'select':
                self._load_favorite(self.myloc, city_id)
                self._save_favorite(self.myloc, city_id)
                self.my_cur_weather()
                self.my_forecast_weather()
                self._update_moon()
                self._update_titles()
                self.instance.invalidate()
            elif action == 'assign':
                fav_index = result[2]  # 0,1,2
                self._save_favorite(fav_index, city_id)
                self.path_loc0 = self._read_favorite('home') or self.path_loc0
                self.path_loc1 = self._read_favorite('fav1') or self.path_loc1
                self.path_loc2 = self._read_favorite('fav2') or self.path_loc2
        else:
            # Fallback
            city_id = result
            self._load_favorite(self.myloc, city_id)
            self._save_favorite(self.myloc, city_id)
            self.my_cur_weather()
            self.my_forecast_weather()
            self._update_moon()
            self._update_titles()
            self.instance.invalidate()

    def Fav0(self):
        self._load_favorite(0, self.path_loc0)

    def Fav1(self):
        self._load_favorite(1, self.path_loc1)

    def Fav2(self):
        self._load_favorite(2, self.path_loc2)

    def _load_favorite(self, fav_index, path_loc):
        """Load data for the specified favorite."""
        self.myloc = fav_index
        day_index = self.tag
        location_id = path_loc.split('/')[0] if '/' in path_loc else path_loc

        # Get location details
        place = self.weather_api.get_location_by_id(location_id)
        if place:
            self.town = place.name
            self.country = place.country_name
            self.lon = str(place.long)
            self.lat = str(place.lat)
            # Get the IANA timezone name from the location (e.g. "Europe/Rome")
            tz_name = place.timezone
            # Check if the timezone exists in the system
            if self.timezones.timezones.get(tz_name.split('/')[0]):  # area
                # Create a timezone object using the time module (approximate conversion)
                # Note: Base Python does not have a real timezone object, but
                # we can calculate the offset
                self.tz_name = tz_name
                # Advanced option: if Python is >= 3.9, zoneinfo can be used
                try:
                    from zoneinfo import ZoneInfo
                    self.tz = ZoneInfo(tz_name)
                except ImportError:
                    # Fallback: calculate the current offset
                    # This is less accurate but works for display purposes
                    self.tz_offset = self._get_timezone_offset(tz_name)
            else:
                self.tz = None
        else:
            self.town = self.country = self.lon = self.lat = 'N/A'

        if DEBUG:
            _write_favorite_debug(
                f"# DEBUG: Location loaded: town={self.town}, country={self.country}, lon={self.lon}, lat={self.lat}")

        # Get current weather
        current = self.weather_api.get_current_weather(location_id)
        if current:
            self.cur_temp = str(current.temp)
            self.fl_temp = str(current.feel_temp)
            self.pic = current.condition
            self.wind = self.degreesToWindDirection(current.wind_direction)
            self.wind_speed = str(
                current.wind_speed) if current.wind_speed is not None else 'N/A'
            self.wind_gust = str(
                current.wind_gust) if current.wind_gust is not None else 'N/A'
            self.rain_mm = str(
                current.precipitation) if current.precipitation is not None else '0.0'
            self.hum = str(
                current.humidity) if current.humidity is not None else 'N/A'
            self.pressure = str(
                current.pressure) if current.pressure is not None else 'N/A'
            self.dewpoint = str(
                current.dewpoint) if current.dewpoint is not None else 'N/A'
            self.uvi = str(current.uvi) if current.uvi is not None else 'N/A'
            self.aqi = str(current.aqi) if current.aqi is not None else 'N/A'
            self.rainp = str(
                current.rainp) if current.rainp is not None else 'N/A'
            self.snowp = str(
                current.snowp) if current.snowp is not None else 'N/A'
            self.updated = str(current.updated) if current.updated else 'N/A'
            # Convert updated to local time
            if self.updated != 'N/A':
                try:
                    utc_dt = datetime.datetime.fromisoformat(
                        self.updated.replace('Z', '+00:00'))
                    local_dt = self.utc_to_local(utc_dt)
                    self.updated = local_dt.strftime("%H:%M %d/%m")
                except Exception as e:
                    if DEBUG:
                        print(f"[Foreca1] Error converting updated: {e}")
            # Debug current weather
            if DEBUG:
                dbg_text = (
                    f"# DEBUG: Current weather for {self.town}:\n"
                    f"Temp: {self.cur_temp}°C, Feels like: {self.fl_temp}°C, Condition: {self.pic}\n"
                    f"Wind: {self.wind} {self.wind_speed} km/h, Gust: {self.wind_gust} km/h\n"
                    f"Humidity: {self.hum}%, Pressure: {self.pressure}, Dewpoint: {self.dewpoint}\n"
                    f"Precipitation: {self.rain_mm} mm, UV Index: {self.uvi}, AQI: {self.aqi}, Rain: {self.rainp}, Snow: {self.snowp}\n"
                    f" updated: Current updated {self.updated}:\n")
                _write_favorite_debug(dbg_text)
        else:
            if DEBUG:
                _write_favorite_debug("# DEBUG: Current weather data is None")
            self.cur_temp = self.fl_temp = self.pic = self.wind = self.wind_speed = self.wind_gust = self.rain_mm = self.hum = self.pressure = self.dewpoint = self.uvi = 'N/A'

        # Daily forecast
        days_needed = max(self.tag + 1, 1)
        daily_all = self.weather_api.get_daily_forecast(
            location_id, days=days_needed)
        if daily_all and len(daily_all) > self.tag:
            day_selected = daily_all[self.tag]

            # --- SUNRISE/SUNSET ---
            self.sunrise = day_selected.sunrise.strftime(
                "%H:%M") if day_selected.sunrise else 'N/A'
            self.sunset = day_selected.sunset.strftime(
                "%H:%M") if day_selected.sunset else 'N/A'
            hours = day_selected.daylength // 60 if day_selected.daylength else 0
            mins = day_selected.daylength % 60 if day_selected.daylength else 0
            self.daylen = _("{hours} h {mins} min").format(
                hours=hours, mins=mins)

            # --- DATA THAT CHANGES WITH THE DAY (present in daily) ---
            # <-- only for tomorrow, the day after tomorrow, etc.
            if self.tag > 0:
                self.cur_temp = str(day_selected.max_temp)
                self.fl_temp = str(day_selected.max_temp)
                self.pic = day_selected.condition
                self.wind = self.degreesToWindDirection(
                    day_selected.wind_direction)
                self.wind_speed = str(day_selected.wind_speed)
                self.rain_mm = str(day_selected.precipitation)
                self.hum = str(day_selected.humidity)
                self.uvi = str(
                    day_selected.uvi) if day_selected.uvi is not None else 'N/A'
                self.rainp = str(
                    day_selected.rainp) if day_selected.rainp is not None else 'N/A'
                self.snowp = str(
                    day_selected.snowp) if day_selected.snowp is not None else 'N/A'
                self.updated = str(
                    day_selected.updated) if day_selected.updated else 'N/A'
        else:
            # Fallback: reset all daily fields (including new ones)
            self.sunrise = self.sunset = self.daylen = 'N/A'
            self.cur_temp = self.fl_temp = self.pic = self.wind = self.wind_speed = self.wind_gust = 'N/A'
            self.rain_mm = self.hum = self.pressure = 'N/A'
            self.uvi = self.aqi = self.rainp = self.snowp = self.updated = 'N/A'
            # self.dewpoint remains untouched

        if DEBUG:
            debug_msg = (
                f"# DEBUG: Daily forecast for day {self.tag}:\n"
                f"sunrise={self.sunrise}, sunset={self.sunset}, daylen={self.daylen}\n"
                f"temp={self.cur_temp}, condition={self.pic}, wind={self.wind} {self.wind_speed}\n"
                f"rain={self.rain_mm}, hum={self.hum}\n"
                f"(current values preserved: uvi={self.uvi}, rainp={self.rainp}, snowp={self.snowp}, updated={self.updated})")
            _write_favorite_debug(debug_msg)

        # Hourly forecast
        hourly = self.weather_api.get_hourly_forecast(
            location_id, day=day_index)
        if hourly:
            self.f_time = [h.time.strftime("%H:%M") for h in hourly]
            self.f_cur_temp = [str(h.temp) for h in hourly]
            self.f_flike_temp = [str(h.feel_temp) for h in hourly]
            self.f_symb = [h.condition for h in hourly]
            self.f_wind = [
                self.degreesToWindDirection(
                    h.wind_direction) for h in hourly]
            self.f_wind_speed = [str(h.wind_speed) for h in hourly]
            # self.f_precipitation = [str(h.precipitation) for h in hourly]
            self.f_precipitation = [
                str(h.precip_prob) if h.precip_prob is not None else '0' for h in hourly]
            self.f_rel_hum = [str(h.humidity) for h in hourly]
            self.f_uvi = [str(h.uvi) if hasattr(h, 'uvi')
                          and h.uvi is not None else 'N/A' for h in hourly]
            target_date = datetime.date.today() + datetime.timedelta(days=day_index)
            self.f_date = [target_date.strftime("%Y-%m-%d")] * len(hourly)
            self.f_day = target_date.strftime("%A")

            # Debug hourly forecast
            if DEBUG:
                for i in range(len(hourly)):
                    _write_favorite_debug(
                        f"# DEBUG: Hour {self.f_time[i]}: Temp={self.f_cur_temp[i]}°C, Feels={self.f_flike_temp[i]}°C, Condition={self.f_symb[i]}, "
                        f"Wind={self.f_wind[i]} {self.f_wind_speed[i]} km/h, Precip={self.f_precipitation[i]}%, Humidity={self.f_rel_hum[i]}%, UV={self.f_uvi[i]}")
        else:
            if DEBUG:
                debug_msg = (
                    f"# DEBUG: Daily forecast for day {self.tag}:\n"
                    f"sunrise={self.sunrise}, sunset={self.sunset}, daylen={self.daylen}\n"
                    f"temp={self.cur_temp}, condition={self.pic}, wind={self.wind} {self.wind_speed}\n"
                    f"rain={self.rain_mm}, hum={self.hum}, uvi={self.uvi}, rainp={self.rainp}, snowp={self.snowp}\n"
                    f"updated={self.updated}")
                _write_favorite_debug(debug_msg)
            self.f_time = self.f_cur_temp = self.f_flike_temp = self.f_symb = self.f_wind = self.f_wind_speed = self.f_precipitation = self.f_rel_hum = self.f_date = self.f_uvi = []
            self.f_day = 'N/A'

        # Update UI
        self._update_moon()
        self.my_cur_weather()
        self.my_forecast_weather()
        self._update_titles()
        if self.lat != 'N/A' and self.lon != 'N/A':
            Thread(target=self.mypicload).start()

    def _read_favorite(self, name):
        path = join(SYSTEM_DIR, f"{name}.cfg")
        if exists(path):
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except BaseException:
                pass
        return None

    def _read_color(self):
        path = join(SYSTEM_DIR, "set_color.conf")
        if exists(path):
            try:
                with open(path, "r") as f:
                    parts = f.read().strip().split()
                    if len(parts) >= 3:
                        return parts[0], parts[1], parts[2]
            except BaseException:
                pass
        return 0, 80, 239

    def _read_alpha(self):
        path = join(SYSTEM_DIR, "set_alpha.conf")
        if exists(path):
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except BaseException:
                pass
        return '#40000000'

    def _save_favorite(self, index, city_id):
        names = ['home', 'fav1', 'fav2']
        if index < 0 or index >= len(names):
            return
        filename = join(SYSTEM_DIR, names[index] + ".cfg")
        try:
            with open(filename, "w") as f:
                f.write(city_id)
            chmod(filename, 0o655)
            if DEBUG:
                print(
                    f"[Foreca1] Saved {names[index]} = {city_id} (perms 655)")
        except Exception as e:
            print(f"[Foreca1] Error saving {names[index]}: {e}")

    def _save_color(self):
        path = join(SYSTEM_DIR, "set_color.conf")
        try:
            with open(path, "w") as f:
                f.write(f"{self.rgbmyr} {self.rgbmyg} {self.rgbmyb}")
            chmod(path, 0o655)
            if DEBUG:
                print(
                    f"[Foreca1] Color saved: {self.rgbmyr} {self.rgbmyg} {self.rgbmyb}")
        except Exception as e:
            print("[Foreca1] Error saving color:", e)

    def _save_alpha(self):
        path = join(SYSTEM_DIR, "set_alpha.conf")
        try:
            with open(path, "w") as f:
                f.write(self.alpha)
            chmod(path, 0o655)
        except Exception as e:
            print("[Foreca1] Error saving alpha:", e)

    def my_cur_weather(self):
        """Update all current weather widgets with actual data using UnitManager."""
        if not self.unit_manager:
            return

        # --- DEBUG RAW DATA ---
        if DEBUG:
            from datetime import datetime
            write_current_weather_debug("\n" + "=" * 60)
            write_current_weather_debug(
                f"UPDATE TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            write_current_weather_debug(f"Town        : {self.town}")
            write_current_weather_debug(
                f"Unit system : {self.unit_manager.get_simple_system()}")
            write_current_weather_debug("RAW DATA:")
            write_current_weather_debug(f"  Temp       = {self.cur_temp}")
            write_current_weather_debug(f"  Feels like = {self.fl_temp}")
            write_current_weather_debug(f"  Dewpoint   = {self.dewpoint}")
            write_current_weather_debug(f"  Condition  = {self.pic}")
            write_current_weather_debug(
                f"  Wind       = {self.wind} {self.wind_speed}")
            write_current_weather_debug(f"  Gust       = {self.wind_gust}")
            write_current_weather_debug(f"  Rain       = {self.rain_mm}")
            write_current_weather_debug(f"  Humidity   = {self.hum}")
            write_current_weather_debug(f"  Pressure   = {self.pressure}")
            write_current_weather_debug(
                f"  UV index   = {getattr(self, 'uvi', 'N/A')}")
            write_current_weather_debug(
                f"  AQI        = {getattr(self, 'aqi', 'N/A')}")
            write_current_weather_debug(
                f"  Rain prob. = {getattr(self, 'rainp', 'N/A')}%")
            write_current_weather_debug(
                f"  Snow prob. = {getattr(self, 'snowp', 'N/A')}%")
            write_current_weather_debug(
                f"  Updated    = {getattr(self, 'updated', 'N/A')}")
            write_current_weather_debug(f"  Sunrise    = {self.sunrise}")
            write_current_weather_debug(f"  Sunset     = {self.sunset}")
            write_current_weather_debug(f"  Day length = {self.daylen}")
            write_current_weather_debug("-" * 60)

        # --- CITY ---
        self["city_name"].setText(self.town if self.town != 'N/A' else "N/A")

        # --- TEMPERATURE ---
        if self.cur_temp != 'N/A':
            temp_val, temp_unit = self.unit_manager.convert_temperature(
                float(self.cur_temp))
            cur_temp_text = "{}{}".format(int(temp_val), temp_unit)
        else:
            cur_temp_text = "N/A"
        self["temperature_current"].setText(cur_temp_text)

        # --- FEELS LIKE ---
        if self.fl_temp != 'N/A':
            fl_val, fl_unit = self.unit_manager.convert_temperature(
                float(self.fl_temp))
            feels_text = _("Feels like {}{}").format(int(fl_val), fl_unit)
        else:
            feels_text = _("Feels like {}").format("N/A")
        self["temperature_feelslike"].setText(feels_text)

        # --- DEWPOINT (always in °C for now, but you could convert) ---
        if self.dewpoint != 'N/A':
            dew_text = _("Dewpoint {}°C").format(self.dewpoint)
        else:
            dew_text = _("Dewpoint {}").format("N/A")
        self["dewpoint_value"].setText(dew_text)

        # --- WIND ---
        if self.wind_speed != 'N/A':
            wind_val, wind_unit = self.unit_manager.convert_wind(
                float(self.wind_speed))
            wind_text = _("Wind speed: {:.1f} {}").format(wind_val, wind_unit)
        else:
            wind_text = _("Wind speed {}").format("N/A")
        self["wind_speed_value"].setText(wind_text)

        # --- WIND GUST ---
        if self.wind_gust != 'N/A':
            gust_val, gust_unit = self.unit_manager.convert_wind(
                float(self.wind_gust))
            gust_text = _("Gust: {:.1f} {}").format(gust_val, gust_unit)
        else:
            gust_text = _("Gust {}").format("N/A")
        self["wind_gust_value"].setText(gust_text)

        # --- PRESSURE ---
        if self.pressure != 'N/A':
            press_val, press_unit = self.unit_manager.convert_pressure(
                float(self.pressure))
            if press_unit == 'inHg':
                press_text = "{:.2f} {}".format(press_val, press_unit)
            else:
                press_text = "{:.0f} {}".format(press_val, press_unit)
        else:
            press_text = "N/A"
        self["pressure_value"].setText(press_text)

        # --- RAIN ---
        if self.rain_mm != 'N/A':
            rain_val, rain_unit = self.unit_manager.convert_precipitation(
                float(self.rain_mm))
            rain_text = _("Rain: {:.1f} {}").format(rain_val, rain_unit)
        else:
            rain_text = "N/A"
        self["rain_value"].setText(rain_text)

        # --- HUMIDITY (no conversion) ---
        if self.hum != 'N/A':
            hum_text = _("Humidity: {}%").format(self.hum)
        else:
            hum_text = "N/A"
        self["humidity_value"].setText(hum_text)

        # --- WEATHER DESCRIPTION ---
        if self.pic != 'N/A':
            desc = _symbol_to_description(self.pic)
            self["weather_description"].setText(trans(desc))
        else:
            self["weather_description"].setText("N/A")

        # --- ICONS ---
        # Weather icon
        if is_valid(self.pic):
            icon_path = join(PLUGIN_PATH, "thumb", f"{self.pic}.png")
            if exists(icon_path):
                self["icon_weather"].instance.setPixmapFromFile(icon_path)
            else:
                fallback = join(PLUGIN_PATH, "thumb", "d000.png")
                if exists(fallback):
                    self["icon_weather"].instance.setPixmapFromFile(fallback)
        else:
            fallback = join(PLUGIN_PATH, "thumb", "d000.png")
            if exists(fallback):
                self["icon_weather"].instance.setPixmapFromFile(fallback)
        self["icon_weather"].instance.show()

        # Wind icon
        if is_valid(self.wind):
            wind_icon_path = join(PLUGIN_PATH, "thumb", f"{self.wind}.png")
            if exists(wind_icon_path):
                self["icon_wind"].instance.setPixmapFromFile(wind_icon_path)
            else:
                fallback = join(PLUGIN_PATH, "thumb", "wN.png")
                if exists(fallback):
                    self["icon_wind"].instance.setPixmapFromFile(fallback)
        else:
            fallback = join(PLUGIN_PATH, "thumb", "wN.png")
            if exists(fallback):
                self["icon_wind"].instance.setPixmapFromFile(fallback)
        self["icon_wind"].instance.show()

        # --- SUNRISE, SUNSET, DAY LENGTH ---
        self["sunrise_value"].setText(
            self.sunrise if self.sunrise != 'N/A' else 'N/A')
        self["sunset_value"].setText(
            self.sunset if self.sunset != 'N/A' else 'N/A')
        self["day_length"].setText(
            self.daylen if self.daylen != 'N/A' else 'N/A')
        self["sunrise_value"].instance.invalidate()
        self["sunset_value"].instance.invalidate()
        self["day_length"].instance.invalidate()

        # --- UV INDEX ---
        if hasattr(self, 'uvi') and self.uvi != 'N/A':
            uvi_val = int(self.uvi)
            uvi_text = f"{_('UV')} {uvi_val}"
            uvi_desc = self.uviToDescription(uvi_val)
            uv_color = self.uviToColor(uvi_val)
        else:
            uvi_text = _("UV N/A")
            uvi_desc = ""
            uv_color = parseColor("#ffffff")

        if "uvi_value" in self:
            self["uvi_value"].setText(uvi_text)
            self["uvi_value"].instance.setForegroundColor(uv_color)
            self["uvi_value"].instance.show()
        if "uvi_desc" in self:
            self["uvi_desc"].setText(uvi_desc)
            self["uvi_desc"].instance.setForegroundColor(uv_color)
            self["uvi_desc"].instance.show()

        # --- AQI ---
        if hasattr(self, 'aqi') and self.aqi != 'N/A':
            self["aqi_value"].setText(_("AQI {}").format(self.aqi))
        else:
            self["aqi_value"].setText(_('AQI: N/A'))

        # --- RAIN PROB ---
        if hasattr(self, 'rainp') and self.rainp != 'N/A':
            self["rainp_value"].setText(_("Rain prob. {}%").format(self.rainp))
        else:
            self["rainp_value"].setText(_('Rain prob.: N/A'))

        # --- SNOW PROB ---
        if hasattr(self, 'snowp') and self.snowp != 'N/A':
            self["snowp_value"].setText(_("Snow prob. {}%").format(self.snowp))
        else:
            self["snowp_value"].setText(_('Snow prob.: N/A'))

        # --- UPDATED ---
        if hasattr(self, 'updated') and self.updated != 'N/A':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(
                    self.updated.replace('Z', '+00:00'))
                updated_str = dt.strftime("%H:%M %d/%m")
                self["updated_label"].setText(
                    _("Updated {}").format(updated_str))
            except BaseException:
                self["updated_label"].setText(
                    _("Updated {}").format(self.updated))
        else:
            self["updated_label"].setText(_('Updated: N/A'))

        # --- DEBUG DISPLAYED VALUES ---
        if DEBUG:
            write_current_weather_debug("DISPLAY VALUES:")
            write_current_weather_debug(f"  Temperature : {cur_temp_text}")
            write_current_weather_debug(f"  Feels like  : {feels_text}")
            write_current_weather_debug(f"  Dewpoint    : {dew_text}")
            write_current_weather_debug(f"  Wind speed  : {wind_text}")
            write_current_weather_debug(f"  Gust        : {gust_text}")
            write_current_weather_debug(f"  Pressure    : {press_text}")
            write_current_weather_debug(f"  Rain        : {rain_text}")
            write_current_weather_debug(f"  Humidity    : {hum_text}")
            write_current_weather_debug(
                f"  Description : {self['weather_description'].getText()}")
            if hasattr(self, 'uvi'):
                write_current_weather_debug(
                    f"  UV index    : {self.uvi} ({uvi_desc})")
            write_current_weather_debug(
                f"  AQI         : {self['aqi_value'].getText()}")
            write_current_weather_debug(
                f"  Rain prob.  : {self['rainp_value'].getText()}")
            write_current_weather_debug(
                f"  Snow prob.  : {self['snowp_value'].getText()}")
            write_current_weather_debug(
                f"  Updated     : {self['updated_label'].getText()}")
            write_current_weather_debug("=" * 60)

    def my_forecast_weather(self):
        """Build the hourly forecast list with unit conversions."""
        # debug (forecast update start)
        if DEBUG:
            from datetime import datetime
            DBG_DIR = join(PLUGIN_PATH, 'debug')
            if not exists(DBG_DIR):
                makedirs(DBG_DIR)
            dbg_path = join(DBG_DIR, "forecast_weather_debug.txt")
            try:
                with open(dbg_path, "a") as dbg:
                    dbg.write("\n" + "=" * 70 + "\n")
                    dbg.write(
                        f"FORECAST UPDATE START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    dbg.write("=" * 70 + "\n")
            except Exception as e:
                print(f"[Foreca1] Forecast debug write error: {e}")

        self.list = []
        n = len(self.f_time)
        if n == 0:
            self["menu"].setList([])
            return

        # Prepare descriptions for batch translation
        descriptions = []
        for symb in self.f_symb:
            if is_valid(symb):
                descriptions.append(_symbol_to_description(str(symb)))
            else:
                descriptions.append("Unknown")
        trans_desc = translate_batch_strings(descriptions)

        for i in range(n):
            # debug (single entry)
            if DEBUG:
                try:
                    with open(dbg_path, "a") as dbg:
                        dbg.write("-" * 60 + "\n")
                        dbg.write(f"INDEX: {i}\n")
                        dbg.write(f"Time: {self.f_time[i]}\n")
                        dbg.write(
                            f"Raw temperature: {self.f_cur_temp[i] if i < len(self.f_cur_temp) else 'N/A'}\n")
                        dbg.write(
                            f"Raw symbol: {self.f_symb[i] if i < len(self.f_symb) else 'N/A'}\n")
                        dbg.write(
                            f"Raw wind direction: {self.f_wind[i] if i < len(self.f_wind) else 'N/A'}\n")
                        dbg.write(
                            f"Raw wind speed: {self.f_wind_speed[i] if i < len(self.f_wind_speed) else 'N/A'}\n")
                        dbg.write(
                            f"Raw feels like: {self.f_flike_temp[i] if i < len(self.f_flike_temp) else 'N/A'}\n")
                        dbg.write(
                            f"Raw precipitation: {self.f_precipitation[i] if i < len(self.f_precipitation) else 'N/A'}\n")
                        dbg.write(
                            f"Raw humidity: {self.f_rel_hum[i] if i < len(self.f_rel_hum) else 'N/A'}\n")
                except Exception as e:
                    print(f"[Foreca1] Forecast debug single entry error: {e}")

            # --- Temperature con conversione ---
            try:
                temp_val = float(self.f_cur_temp[i])
                if self.unit_manager:
                    converted, unit = self.unit_manager.convert_temperature(
                        temp_val)
                    temp_str = f"{int(converted)}{unit}"
                else:
                    temp_str = f"+{int(temp_val)}" if temp_val >= 0 else str(
                        int(temp_val)) + "°C"
            except BaseException:
                temp_str = "N/A"

            # Weather icon
            symb = self.f_symb[i] if i < len(self.f_symb) else 'n600'
            icon_path = resolveFilename(
                SCOPE_PLUGINS, f"Extensions/Foreca1/thumb/{symb}.png")
            if exists(icon_path):
                icon_meteo = LoadPixmap(cached=True, path=icon_path)
            else:
                icon_meteo = LoadPixmap(
                    cached=True, path=resolveFilename(
                        SCOPE_PLUGINS, "Extensions/Foreca1/thumb/n600.png"))

            # Wind direction
            try:
                wind_dir_str = self.f_wind[i] if i < len(self.f_wind) else "wN"
                wind_icon_path = resolveFilename(
                    SCOPE_PLUGINS, f"Extensions/Foreca1/thumb/{wind_dir_str}.png")
                if exists(wind_icon_path):
                    icon_wind = LoadPixmap(cached=True, path=wind_icon_path)
                else:
                    icon_wind = LoadPixmap(
                        cached=True, path=resolveFilename(
                            SCOPE_PLUGINS, "Extensions/Foreca1/thumb/wN.png"))
            except BaseException:
                wind_dir_str = "w360"

            # --- Wind speed con conversione ---
            try:
                speed = float(self.f_wind_speed[i])  # in m/s
                if self.unit_manager:
                    converted, unit = self.unit_manager.convert_wind(speed)
                    wind_speed_str = f"{int(converted)} {unit}"
                else:
                    wind_speed_str = f"{int(speed * 3.6)} km/h"
            except BaseException:
                wind_speed_str = "N/A"

            # --- Feels like con conversione ---
            try:
                fl_val = float(self.f_flike_temp[i])
                if self.unit_manager:
                    converted, unit = self.unit_manager.convert_temperature(
                        fl_val)
                    fl_str = f"{int(converted)}{unit}"
                else:
                    fl_str = f"+{int(fl_val)}" if fl_val >= 0 else str(int(fl_val)) + "°C"
            except BaseException:
                fl_str = "N/A"
            feels_like_str = _("Feels like: {}").format(fl_str)

            # Precipitation
            precip = self.f_precipitation[i] if i < len(
                self.f_precipitation) else '0'
            precip_str = _("Precipitations: {}%").format(precip)

            # Humidity
            hum = self.f_rel_hum[i] if i < len(self.f_rel_hum) else '0'
            hum_str = _("Humidity: {}%").format(hum)
            self.list.append((
                self.f_time[i],        # 0
                _('Temp'),             # 1
                icon_wind,             # 2  <-- wind icon
                temp_str,              # 3
                icon_meteo,            # 4  <-- meteo icon
                _('Wind'),             # 5
                wind_speed_str,        # 6
                trans_desc[i],         # 7
                feels_like_str,        # 8
                precip_str,            # 9
                hum_str                # 10
            ))

        # Update the menu list
        self["menu"].setList(self.list)

        # Start station update in background
        Thread(target=self._update_station_label).start()

        # debug (forecast update end)
        if DEBUG:
            from datetime import datetime
            try:
                with open(dbg_path, "a") as dbg:
                    dbg.write(
                        f"FORECAST UPDATE END: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    dbg.write("=" * 70 + "\n\n")
            except Exception as e:
                print(f"[Foreca1] Forecast debug write error: {e}")

    def update_me(self):
        """Checks for updates and asks for confirmation to install them."""
        import requests
        try:
            resp = requests.get(INSTALLER_URL, timeout=10)
            if resp.status_code != 200:
                self.session.open(
                    MessageBox,
                    _("Could not fetch update information."),
                    MessageBox.TYPE_ERROR)
                return

            data = resp.text
            remote_version = None
            remote_changelog = ""
            for line in data.splitlines():
                if line.startswith("version="):
                    # assume format: version='1.0.0' or version="1.0.0"
                    if "'" in line:
                        remote_version = line.split("'")[1]
                    else:
                        remote_version = line.split("=")[1].strip().strip('"')
                elif line.startswith("changelog="):
                    if "'" in line:
                        remote_changelog = line.split("'")[1]
                    else:
                        remote_changelog = line.split(
                            "=")[1].strip().strip('"')

            if remote_version is None:
                self.session.open(
                    MessageBox,
                    _("Could not parse version information."),
                    MessageBox.TYPE_ERROR)
                return

            current_version = VERSION

            # helper function to compare versions like "1.0.0"
            def version_tuple(v):
                return tuple(map(int, v.split('.')))
            if version_tuple(remote_version) > version_tuple(current_version):
                msg = _("New version {version} is available.").format(
                    version=remote_version) + "\n"
                if remote_changelog:
                    msg += _("Changelog: {changelog}").format(
                        changelog=remote_changelog) + "\n"
                msg += _("Do you want to install it now?")
                self.session.openWithCallback(
                    lambda answer: self.install_update(answer, INSTALLER_URL),
                    MessageBox,
                    msg,
                    MessageBox.TYPE_YESNO
                )
            else:
                self.session.open(
                    MessageBox,
                    _("You already have the latest version."),
                    MessageBox.TYPE_INFO,
                    timeout=4)
        except Exception as e:
            print("[Foreca1] Update check error:", e)
            self.session.open(
                MessageBox,
                _("Error checking for updates."),
                MessageBox.TYPE_ERROR)

    def install_update(self, answer, installer_url):
        """Runs the update script if the user confirmed."""
        if answer:
            cmd = f"wget -q --no-check-certificate {installer_url} -O - | /bin/sh"
            from Screens.Console import Console
            self.session.open(
                Console,
                _("Updating..."),
                cmdlist=[cmd],
                finishedCallback=self.update_finished,
                closeOnSuccess=True
            )
        else:
            self.session.open(
                MessageBox,
                _("Update canceled."),
                MessageBox.TYPE_INFO,
                timeout=3)

    def update_finished(self, result=None):
        """Callback executed when the installation finishes."""
        self.session.open(
            MessageBox,
            _("Update completed. Please restart Enigma2."),
            MessageBox.TYPE_INFO)

    def _update_titles(self):
        date_str = str(self.f_date[0]) if self.f_date else _(
            "No date available")
        day_str = trans(self.f_day) if is_valid(self.f_day) else ""
        title_text = f"{self.town}, {trans(self.country)} - {date_str}"
        if day_str:
            title_text += f" - {day_str}"
        self["title_main"].text = title_text
        self["title_section_weather"].text = _("Current weather and forecast")
        self["title_version"].text = f"Foreca One\n| v.{VERSION} |"
        self["maintener"].text = "by @lululla\n| 2026 |"
        self["title_loading"].text = ""

    def update_time(self):
        # Use the city's timezone if available
        now = datetime.datetime.now()
        if hasattr(self, 'tz') and self.tz:
            now = now.astimezone(self.tz)
        elif hasattr(self, 'tz_offset'):
            # Calculate offset manually? Better to use datetime.timezone
            tz = datetime.timezone(datetime.timedelta(hours=self.tz_offset))
            now = now.astimezone(tz)
        time_str = now.strftime("%H:%M:%S")
        self["current_time"].setText(time_str)

    def _update_button(self):
        if DEBUG:
            print("[DEBUG] update_button() called")
            print(
                "[DEBUG] self.rgbmyr, g, b =",
                self.rgbmyr,
                self.rgbmyg,
                self.rgbmyb)
        self.color = gRGB(int(self.rgbmyr), int(self.rgbmyg), int(self.rgbmyb))
        for name in [
            "selection_overlay",
            "background_plate",
            "color_bg_today",
            "color_bg_forecast",
            "color_bg_sun",
                "color_bg_coords"]:
            if name in self:
                if DEBUG:
                    print(f"[DEBUG] {name} exists")
                if self[name].instance:
                    if DEBUG:
                        print(f"[DEBUG] {name} instance OK")
                    self[name].instance.setBackgroundColor(self.color)
                    self[name].instance.invalidate()
                else:
                    print(
                        f"[DEBUG] {name} instance is None (widget non creato dalla skin?)")
            else:
                print(f"[DEBUG] {name} NOT in self (manca nella skin?)")

        transparent_color = parseColor(self.alpha)
        for name in [
            "transp_bg_today",
            "transp_bg_forecast",
            "transp_bg_sun",
            "transp_bg_coords",
                "transp_bg_header"]:
            if name in self:
                if self[name].instance:
                    self[name].instance.setBackgroundColor(transparent_color)
                    self[name].instance.invalidate()
                else:
                    print(f"[DEBUG] {name} instance is None")
        self.instance.invalidate()

    def _update_station_label(self):
        """Update the nearest station name (if available) using auth API or scraping."""
        location_id = [self.path_loc0, self.path_loc1,
                       self.path_loc2][self.myloc].split('/')[0]
        if not location_id:
            return

        station_text = _("No station data")
        source = None

        # Function to truncate long text
        def truncate(text, max_len=25):
            if len(text) > max_len:
                return text[:max_len - 3] + "..."
            return text

        # 1. Try with authenticated API (if available)
        if hasattr(self, 'weather_api_auth') and self.weather_api_auth:
            try:
                observations = self.weather_api_auth.get_station_observations(
                    location_id, station_limit=1)
                if observations and len(observations) > 0:
                    obs = observations[0]
                    station_name = obs.get('station', 'N/A')
                    distance = obs.get('distance', '')
                    if distance:
                        station_text = f"{station_name} ({distance})"
                    else:
                        station_text = station_name
                    source = "API"
            except Exception as e:
                print(f"[Foreca1] Auth station error: {e}")

        # 2. Fallback to scraping (via free API)
        if station_text == _("No station data") and hasattr(
                self.weather_api, 'get_nearby_stations_scraped'):
            try:
                stations = self.weather_api.get_nearby_stations_scraped(
                    location_id)
                if stations and len(stations) > 0:
                    first = stations[0]
                    station_name = first.get('station', 'N/A')
                    time_ago = first.get('time_ago', '')
                    if time_ago:
                        station_text = f"{station_name} ({time_ago})"
                    else:
                        station_text = station_name
                    source = _("Scraped")
            except Exception as e:
                print(f"[Foreca1] Scraping station error: {e}")

        # Truncate text if too long
        station_text = truncate(station_text)

        self["station_name"].setText(station_text)
        if source:
            print(f"[Foreca1] Station source: {source}")

    def _update_moon(self):
        info = self.moon.get_phase_info()
        phase_name = info["name"]
        illumination = info["illumination"]
        icon_path = info["icon_path"]

        if "icon_moon" in self and icon_path:
            self["icon_moon"].instance.setPixmapFromFile(icon_path)
        if "moon_label" in self:
            self["moon_label"].setText(_(phase_name))
        if "moon_illum" in self:
            self["moon_illum"].setText(
                _("Visibility") + f" {illumination:.1f}%")
        if "moon_distance" in self:
            distance = self.moon.get_moon_distance()
            self["moon_distance"].setText(_("Distance {} km").format(distance))

        if self.lat != 'N/A' and self.lon != 'N/A':
            # Calculate offset in hours for the location
            offset_hours = None
            if hasattr(self, 'tz_offset'):
                offset_hours = self.tz_offset
            elif hasattr(self, 'tz'):
                from datetime import datetime
                offset_hours = self.tz.utcoffset(
                    datetime.now()).total_seconds() / 3600
            self.moon.get_moon_data_async(
                float(self.lat), float(self.lon),
                callback=self._moon_api_callback,
                offset_hours=offset_hours
            )
        else:
            if "moonrise_value" in self:
                self["moonrise_value"].setText("N/A")
            if "moonset_value" in self:
                self["moonset_value"].setText("N/A")

    def _moon_api_callback(self, api_data):
        if api_data:
            from twisted.internet import reactor

            def update_ui():
                if "moonrise_value" in self and api_data.get(
                        "rise", "N/A") != "N/A":
                    self["moonrise_value"].setText(api_data["rise"])
                if "moonset_value" in self and api_data.get(
                        "set", "N/A") != "N/A":
                    self["moonset_value"].setText(api_data["set"])

                info = self.moon.get_phase_info()
                if "icon_moon" in self and info["icon_path"]:
                    self["icon_moon"].instance.setPixmapFromFile(
                        info["icon_path"])
                if "moon_label" in self:
                    self["moon_label"].setText(_(info["name"]))
                if "moon_illum" in self:
                    self["moon_illum"].setText(
                        _("Illumination") + f" {info['illumination']:.1f}%")
                if "moon_distance" in self:
                    distance = self.moon.get_moon_distance()
                    self["moon_distance"].setText(
                        _("Distance {} km").format(distance))

            reactor.callFromThread(update_ui)

    def open_foreca_api_maps(self, callback=None):
        if not exists(CONFIG_FILE):
            self.session.open(
                MessageBox,
                _("API configuration file not found!\n\nPlease create file:\n{0}\n\nwith your Foreca API credentials.").format(CONFIG_FILE),
                MessageBox.TYPE_ERROR,
                timeout=10)
            return
        try:
            # Use the currently selected location (self.myloc)
            current_path = [self.path_loc0,
                            self.path_loc1, self.path_loc2][self.myloc]
            location_id = current_path.split(
                '/')[0] if '/' in current_path else current_path
            region = self.determine_region_from_location(
                location_id=location_id,
                country_name=self.country,
                lon=self.lon,
                lat=self.lat
            )
            if DEBUG:
                print(
                    f"[DEBUG] Opening ForecaMapMenu with region='{region}', unit_system='{self.unit_manager.get_simple_system()}'")
            api = ForecaMapAPI(region=region)
            if not api.check_credentials():
                self.session.open(
                    MessageBox,
                    _("API credentials not configured."),
                    MessageBox.TYPE_ERROR)
                return
            if callback:
                self.session.openWithCallback(
                    callback,
                    ForecaMapMenu,
                    api,
                    self.unit_manager.get_simple_system(),
                    region)
            else:
                self.session.open(
                    ForecaMapMenu,
                    api,
                    self.unit_manager.get_simple_system(),
                    region)
        except Exception as e:
            print("[Foreca1] Error opening API maps:", e)
            self.session.open(
                MessageBox,
                _("Could not initialize map API."),
                MessageBox.TYPE_ERROR)

    def open_maps_menu(self):
        maps_menu = [
            (_("Weather Maps (Wetterkontor)"), "wetterkontor"),
            (_("Foreca One Live Maps (API)"), "foreca_api"),
            (_("Satellite Photos"), "satellite")
        ]
        self.session.openWithCallback(
            self.maps_menu_callback,
            ChoiceBox,
            title=_("Weather Maps & Satellite"),
            list=maps_menu
        )

    def open_daily_forecast(self):
        location_id = [self.path_loc0, self.path_loc1,
                       self.path_loc2][self.myloc].split('/')[0]
        location_name = self.town
        if not location_id:
            self.session.open(
                MessageBox,
                _("No location selected"),
                MessageBox.TYPE_INFO)
            return
        self.session.open(
            DailyForecast,
            self.weather_api,
            location_id,
            location_name)

    def open_meteogram(self):
        # debug: start opening meteogram
        if DEBUG:
            write_meteogram_debug(
                f"[DEBUG] open_meteogram called - myloc={self.myloc}, town={self.town}")

        location_id = [self.path_loc0, self.path_loc1,
                       self.path_loc2][self.myloc].split('/')[0]
        location_name = self.town

        # debug: location info
        if DEBUG:
            write_meteogram_debug(
                f"[DEBUG] location_id={location_id}, location_name={location_name}")

        if not location_id:
            self.session.open(
                MessageBox,
                _("No location selected"),
                MessageBox.TYPE_INFO)
            return
        self.session.open(
            MeteogramView,
            self.weather_api,
            location_id,
            location_name,
            self.unit_manager,
            getattr(self, 'tz', None),
            getattr(self, 'tz_offset', None)
        )
        if DEBUG:
            write_meteogram_debug("[DEBUG] MeteogramView opened successfully")

    def open_station_observations(self):
        location_id = [self.path_loc0, self.path_loc1,
                       self.path_loc2][self.myloc].split('/')[0]
        location_name = self.town
        if not location_id:
            self.session.open(
                MessageBox,
                _("No location selected"),
                MessageBox.TYPE_INFO)
            return
        self.session.open(
            ForecaStations,
            # free API (for scraping)
            self.weather_api,
            # authenticated API (if exists)
            getattr(self, 'weather_api_auth', None),
            location_id,
            location_name,
            self.unit_manager
        )

    def after_main_menu(self, result=None):
        """Callback to return to the main menu after closing a screen."""
        self.Menu()

    def after_city(self, result=None):
        self.Menu()

    def after_daily(self, result=None):
        self.Menu()

    def after_meteogram(self, result=None):
        self.Menu()

    def after_stations(self, result=None):
        self.Menu()

    def after_color(self, result=None):
        self.Menu()

    def after_transparency(self, result=None):
        self.Menu()

    def after_maps_menu(self, result=None):
        self.open_maps_menu()

    def after_info(self, result=None):
        self.Menu()

    def after_units(self, result=None):
        """Callback after closing unit settings: Refresh UI if needed."""
        if result:
            self.my_cur_weather()
            self.my_forecast_weather()
            self._update_moon()
            self._update_titles()

    def maps_menu_callback(self, choice):
        if choice is None:
            return
        key = choice[1]
        if key == "wetterkontor":
            self.session.openWithCallback(
                self.after_maps_menu, ForecaMapsMenu, 'europe')
        elif key == "foreca_api":
            self.open_foreca_api_maps(callback=self.after_maps_menu)
        elif key == "satellite":
            self.session.openWithCallback(
                self.after_maps_menu,
                MessageBox,
                _("Satellite photos coming soon!"),
                MessageBox.TYPE_INFO)

    def determine_region_from_location(
            self, location_id, country_name, lon, lat):
        try:
            if lon and lat and lon != 'N/A' and lat != 'N/A':
                lon_float = float(lon)
                lat_float = float(lat)
                if DEBUG:
                    print(
                        f"[DEBUG] determine_region: lon={lon_float}, lat={lat_float}")
                if -125.0 <= lon_float <= -66.0 and 24.0 <= lat_float <= 49.0:
                    if DEBUG:
                        print("[DEBUG] -> us (by coordinates)")
                    return 'us'
        except BaseException:
            pass
        country_lower = str(country_name).lower()
        us_countries = [
            'united states',
            'usa',
            'u.s.a',
            'u.s.',
            'america',
            'canada',
            'mexico']
        if any(us in country_lower for us in us_countries):
            if DEBUG:
                print("[DEBUG] -> us (by country name)")
            return 'us'
        if DEBUG:
            print("[DEBUG] -> eu (default)")
        return 'eu'

    def degreesToWindDirection(self, degrees):
        """Convert wind direction in degrees to cardinal code like wN, wNE, etc."""
        try:
            deg = int(degrees) % 360
            if deg == 0:
                return "wN"
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            index = round(deg / 45) % 8
            return "w" + directions[index]
        except BaseException:
            return "wN"

    def uviToDescription(self, uvi):
        """Convert UV index to descriptive category."""
        try:
            uvi_val = int(uvi)
        except BaseException:
            return _("Unknown")
        if uvi_val <= 2:
            return _("Low")
        elif uvi_val <= 5:
            return _("Moderate")
        elif uvi_val <= 7:
            return _("High")
        elif uvi_val <= 10:
            return _("Very high")
        else:
            return _("Extreme")

    def uviToColor(self, uvi):
        """Return a color based on UV index intensity."""
        try:
            uvi_val = int(uvi)
        except BaseException:
            return parseColor("#ffffff")
        if uvi_val <= 2:
            return parseColor("#00ff00")  # green
        elif uvi_val <= 5:
            return parseColor("#ffff00")  # yellow
        elif uvi_val <= 7:
            return parseColor("#ff9900")  # orange
        elif uvi_val <= 10:
            return parseColor("#ff0000")  # red
        else:
            return parseColor("#9900ff")  # purple

    def _get_timezone_offset(self, tz_name):
        """Calculate the current UTC offset for a given timezone (in hours)."""
        import subprocess
        try:
            # Use the 'date' command with TZ environment variable to get offset
            output = subprocess.check_output(
                ["date", "+%z"], env={"TZ": tz_name}, universal_newlines=True).strip()
            # output is like "+0200" or "-0500"
            if output and len(output) == 5:
                sign = 1 if output[0] == '+' else -1
                hours = int(output[1:3])
                minutes = int(output[3:5])
                offset = hours + minutes / 60.0
                return sign * offset
            else:
                return 0
        except Exception as e:
            print(f"[Foreca] Error getting timezone offset for {tz_name}: {e}")
            return 0

    def utc_to_local(self, utc_dt):
        """Converts a UTC datetime into the city's local time."""
        if not utc_dt:
            return utc_dt
        if hasattr(self, 'tz') and self.tz:
            # Use zoneinfo if available
            return utc_dt.astimezone(self.tz)
        elif hasattr(self, 'tz_offset'):
            # Fallback: add the offset
            return utc_dt + datetime.timedelta(seconds=self.tz_offset * 3600)
        else:
            return utc_dt  # No conversion

    def exit(self):
        """Exit and save configurations."""
        self._save_color()
        self._save_alpha()
        self.close()

    def close(self):
        self.time_timer.stop()
        super(Foreca_Preview, self).close()


def checkInternet():
    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(
            socket.AF_INET, socket.SOCK_STREAM).connect(
            ('8.8.8.8', 53))
        return True
    except BaseException:
        return False


def main(session, **kwargs):
    if not checkInternet():
        session.open(
            MessageBox,
            _("No Internet connection detected."),
            MessageBox.TYPE_INFO)
        return
    session.open(Foreca_Preview)


def Plugins(path, **kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [
        PluginDescriptor(
            name=_("Foreca One") + " ver." + str(VERSION),
            description=_("Current weather and forecast for the next 10 days"),
            icon="plugin.png",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main
        )
    ]
