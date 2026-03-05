#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# MoonPhase.py - Astronomical constants

import glob
import time
import datetime
from os.path import exists, join, isdir, basename
from time import mktime, localtime
from math import pi, cos, radians
from threading import Thread
import requests

from . import _


MOON_PHASES = {
    "New Moon": _("New Moon"),
    "Waxing Crescent": _("Waxing Crescent"),
    "First Quarter": _("First Quarter"),
    "Waxing Gibbous": _("Waxing Gibbous"),
    "Full Moon": _("Full Moon"),
    "Waning Gibbous": _("Waning Gibbous"),
    "Last Quarter": _("Last Quarter"),
    "Waning Crescent": _("Waning Crescent"),
}


class MoonPhase:
    # Astronomical constants
    SYNODIC_MONTH = 29.530588853  # days between two new moons
    # Reference date: New Moon on January 6, 2000 at 00:00 UTC
    NEW_MOON_REF = (2000, 1, 6, 0, 0, 0, 0, 0, 0)  # struct_time

    def __init__(self, icon_path=None, total_icons=31):
        """
        icon_path: absolute path to the folder containing the icons (moon1.png ... moonN.png)
        total_icons: total number of icons (default 32)
        """
        self.icon_path = icon_path
        self.total_icons = total_icons
        # Phase names in English (approximate, you can modify them)
        self.phase_names_en = {
            (0.0, 0.03): _("New Moon"),
            (0.03, 0.22): _("Waxing Crescent"),
            (0.22, 0.28): _("First Quarter"),
            (0.28, 0.47): _("Waxing Gibbous"),
            (0.47, 0.53): _("Full Moon"),
            (0.53, 0.72): _("Waning Gibbous"),
            (0.72, 0.78): _("Last Quarter"),
            (0.78, 0.97): _("Waning Crescent"),
            (0.97, 1.0): _("New Moon")
        }

    def _get_current_phase_value(self):
        """Calculates the current lunar phase (0-1, 0 = New Moon)"""
        # Seconds from epoch to the reference date
        ref_time = mktime(self.NEW_MOON_REF)
        ref_days = ref_time / 86400.0

        # Current time in days
        now_days = mktime(localtime()) / 86400.0

        # Days passed since the reference
        days_since_ref = now_days - ref_days

        # Fraction of the synodic cycle (0-1)
        phase = (days_since_ref % self.SYNODIC_MONTH) / self.SYNODIC_MONTH
        return phase

    def _illumination_from_phase(self, phase):
        """Returns the illumination percentage (0-100) given the phase (0-1, 0 = new)"""
        # Formula: illumination = (1 - cos(2π * phase)) / 2
        return (1 - cos(2 * pi * phase)) / 2 * 100

    def _get_phase_name(self, phase):
        for (low, high), name in self.phase_names_en.items():
            if low <= phase < high:
                return MOON_PHASES.get(name, name)
        return MOON_PHASES["New Moon"]

    def get_phase_info(self):
        """
        Returns a dictionary with:
            - phase: phase value (0-1, 0 = new)
            - illumination: illumination percentage (0-100)
            - name: phase name in English
            - icon_number: most suitable icon number (1..total_icons)
            - icon_path: full path to the PNG file
        """
        phase = self._get_current_phase_value()
        illum = self._illumination_from_phase(phase)
        name = self._get_phase_name(phase)

        # Maps illumination to icon number (1 = full, total_icons = new)
        # illum = 100% → icon 1, illum = 0% → icon total_icons
        # Formula: icon_number = 1 + round( (100 - illum) * (total_icons-1) / 100 )
        icon_number = 1 + round((100 - illum) * (self.total_icons - 1) / 100)
        # Ensure it stays within 1..total_icons
        icon_number = max(1, min(self.total_icons, icon_number))

        icon_file = None
        if self.icon_path:
            # Build full path (e.g., moon12.png)
            icon_file = join(self.icon_path, f"moon{icon_number}.png")
            # If the file does not exist, look for the nearest PNG (safety
            # fallback)
            if not exists(icon_file):
                icon_file = self._find_nearest_icon(icon_number)

        return {
            "phase": phase,
            "illumination": illum,
            "name": name,
            "icon_number": icon_number,
            "icon_path": icon_file
        }

    def _get_julian_day(self, t=None):
        """Julian day for time t (in seconds) or current time."""
        if t is None:
            t = mktime(localtime())
        # Simplified JD formula (valid after 1900)
        # Uses the time library to obtain an accurate date
        dt = datetime.datetime.utcfromtimestamp(t)
        year = dt.year
        month = dt.month
        day = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
        if month <= 2:
            year -= 1
            month += 12
        A = year // 100
        B = 2 - A + A // 4
        JD = int(365.25 * (year + 4716)) + \
            int(30.6001 * (month + 1)) + day + B - 1524.5
        return JD

    def _get_moon_mean_anomaly(self, JD):
        """Moon mean anomaly in degrees."""
        T = (JD - 2451545.0) / 36525.0  # Julian centuries since J2000
        M = 134.963 + 477198.867 * T + 0.008997 * T**2  # degrees
        return radians(M % 360)

    def get_moon_data_async(
            self,
            lat,
            lon,
            callback,
            max_days=2,
            offset_hours=None):
        """Executes the API request in a separate thread and calls a callback with the results."""
        def worker():
            result = self.get_moon_data_from_api(
                lat, lon, max_days, offset_hours)
            if callback:
                callback(result)
        Thread(target=worker).start()

    def get_moon_data_from_api(self, lat, lon, max_days=2, offset_hours=None):
        """
        Searches for moonrise and moonset in the following days (up to max_days)
        to ensure the next moonset is found, even if it occurs after midnight.
        Returns a dictionary with rise, set, phase, illumination.
        """
        if offset_hours is None:
            offset_hours = self._get_offset_hours()
        try:
            base_date = datetime.date.today()
            moonrise = "N/A"
            moonset = "N/A"
            phase_name = "N/A"
            illumination = None

            for days_offset in range(max_days + 1):
                check_date = base_date + datetime.timedelta(days=days_offset)
                date_str = check_date.strftime("%Y-%m-%d")

                url = "https://aa.usno.navy.mil/api/rstt/oneday"
                params = {
                    "date": date_str,
                    "coords": f"{lat}, {lon}",
                    "tz": str(offset_hours),
                    "dst": "false"
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    continue

                data = response.json()
                props = data.get("properties", {}).get("data", {})
                if not props:
                    continue

                for item in props.get("moondata", []):
                    phen = item.get("phen", "")
                    time_val = item.get("time", "N/A")
                    if phen == "Rise" and moonrise == "N/A":
                        moonrise = time_val
                    elif phen == "Set" and moonset == "N/A":
                        moonset = time_val

                if moonrise != "N/A" and moonset != "N/A":
                    if days_offset == 0:
                        phase_name = props.get("curphase", "N/A")
                        illum_str = props.get(
                            "fracillum", "0%").replace(
                            "%", "").strip()
                        illumination = float(
                            illum_str) / 100.0 if illum_str != "N/A" else None
                    break

            return {
                "rise": moonrise,
                "set": moonset,
                "phase": phase_name,
                "illumination": illumination
            }
        except Exception as e:
            print(f"[Moon] Exception: {e}")
            return None

    def _get_offset_hours(self):
        """Calculates the current UTC offset in hours using the time module."""
        lt = time.localtime()
        if lt.tm_isdst > 0:
            offset_sec = -time.altzone
        else:
            offset_sec = -time.timezone
        return round(offset_sec / 3600.0, 1)

    def get_moon_distance(self):
        """
        Calculates the approximate Earth-Moon distance in km.
        Formula based on the Moon's mean anomaly (Chapront).
        Accuracy: error less than 1000 km (more than sufficient).
        """
        # Reference date J2000 (January 1, 2000, 12:00 UTC)
        J2000 = 2451545.0
        # Seconds since 1970-01-01 00:00 UTC
        now = mktime(localtime())
        # Approximate Julian days (formula valid after 1970)
        jd = 2440587.5 + now / 86400.0
        # Julian centuries since J2000
        T = (jd - J2000) / 36525.0

        # Moon mean anomaly in degrees (Chapront formula)
        M = 134.963 + 477198.867 * T + 0.008997 * T**2
        M_rad = radians(M % 360)  # Normalize and convert to radians

        # Distance in km (empirical formula)
        dist_km = (385000.56
                   - 20905.355 * cos(M_rad)
                   - 3699.111 * cos(2 * M_rad)
                   - 2955.968 * cos(3 * M_rad)
                   - 569.925 * cos(4 * M_rad))
        return round(dist_km)

    def get_moon_rise_set_approx(self, lat, lon, date=None):
        """
        Calculates approximate moonrise and moonset times.
        WARNING: this implementation is highly simplified and not very accurate.
        A full implementation would require a complex iterative algorithm.
        Returns a tuple (rise, set) in UTC time or None.
        """
        # A proper implementation would require a library such as ephem or skyfield.
        # Leaving a placeholder.
        return None, None

    def _find_nearest_icon(self, target_num):
        """
        Searches in the icon folder for the file moonX.png with X closest to target_num.
        Returns the path of the found file, or None.
        """
        if not self.icon_path or not isdir(self.icon_path):
            return None
        pattern = join(self.icon_path, "moon*.png")
        files = glob.glob(pattern)
        numbers = []
        for f in files:
            base = basename(f)
            # Extract the number from "moon123.png"
            num_str = base.replace('moon', '').replace('.png', '')
            if num_str.isdigit():
                numbers.append((int(num_str), f))
        if not numbers:
            return None
        # Find the closest number
        nearest = min(numbers, key=lambda x: abs(x[0] - target_num))
        return nearest[1]
