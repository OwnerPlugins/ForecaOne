#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# MoonPhase.py - Astronomical constants with precise calculations

import glob
import time
import datetime
from os.path import exists, join, isdir, basename
from time import mktime, localtime
from math import pi, cos, radians, sin
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

    def __init__(self, icon_path=None, total_icons=101):
        """
        icon_path: absolute path to the folder containing the icons (moon0000.png ... moon0100.png)
        total_icons: total number of icons (default 101, from 0 to 100)
        """
        self.icon_path = icon_path
        self.total_icons = total_icons
        self.api_data = None  # stores data obtained from the USNO API

    def _moon_phase_to_icon(self, phase_name, illum_percent):
        """
        Maps the phase name and illumination percentage (0-100)
        to the icon index (0-100) according to your icon sequence.
        """

        # Indicative centers of the main phases
        phase_centers = {
            "New Moon": 0,
            "Waxing Crescent": 12,
            "First Quarter": 25,
            "Waxing Gibbous": 37,
            "Full Moon": 50,
            "Waning Gibbous": 62,
            "Last Quarter": 75,
            "Waning Crescent": 87,
        }

        # Special cases with linear variation
        if phase_name == "New Moon":
            # Very close to 0% or 100%
            return 0 if illum_percent < 10 else 100

        elif phase_name == "Waxing Crescent":
            # illum from 0% to 50% -> icons from 0 to 25
            return int(illum_percent * 25 / 50)

        elif phase_name == "First Quarter":
            return 25

        elif phase_name == "Waxing Gibbous":
            # illum from 50% to 100% -> icons from 25 to 50
            return int(25 + (illum_percent - 50) * 25 / 50)

        elif phase_name == "Full Moon":
            return 50

        elif phase_name == "Waning Gibbous":
            # illum from 100% to 50% -> icons from 50 to 75
            return int(50 + (100 - illum_percent) * 25 / 50)

        elif phase_name == "Last Quarter":
            return 75

        elif phase_name == "Waning Crescent":
            # illum from 50% to 0% -> icons from 75 to 100
            return int(75 + (50 - illum_percent) * 25 / 50)

        else:
            # fallback to center
            return phase_centers.get(phase_name, 50)

    # -------------------------------------------------------------------------
    # Precise lunar calculations (based on Meeus / external code)
    # -------------------------------------------------------------------------

    def _date_to_jd(self, dt):
        """
        Convert a datetime object to Julian Day (approximate).
        Usa lo stesso metodo di MoonCalendar per coerenza.
        """
        return dt.toordinal() + 1721424.5

    def _compute_lunar_data(self, jd):
        """
        Computes precise lunar data for a given Julian Day (geocentric).
        Returns a dictionary with illumination, phase_name, distance, trend.
        """
        T = (jd - 2451545.0) / 36525.0

        # Mean elements (degrees)
        Dm = (
            297.8501921
            + 445267.114034 * T
            - 0.0018819 * T * T
            + T * T * T / 545868
            - T * T * T * T / 113065000
        )

        Ms = (
            357.5291092
            + 35999.0502909 * T
            - 0.0001536 * T * T
            + T * T * T / 24490000
        )

        Mm = (
            134.9633964
            + 477198.8675055 * T
            + 0.0087414 * T * T
            + T * T * T / 69699
            - T * T * T * T / 14712000
        )

        Fm = (
            93.272095
            + 483202.0175233 * T
            - 0.0036539 * T * T
            - T * T * T / 3526000
            + T * T * T * T / 863310000
        )

        # Eccentricity factor
        E = 1 - 0.002516 * T - 0.0000074 * T * T

        # Distance correction (ER)
        ER = (
            -20.905355 * cos(radians(Mm))
            - 3.699111 * cos(radians(2 * Dm - Mm))
            - 2.955968 * cos(radians(2 * Dm))
            - 0.569925 * cos(radians(2 * Mm))
            + 0.048888 * cos(radians(Ms)) * E
            - 0.003149 * cos(radians(2 * Fm))
            + 0.246158 * cos(radians(2 * Dm - 2 * Mm))
            - 0.152138 * cos(radians(2 * Dm - Ms - Mm)) * E
            - 0.170733 * cos(radians(2 * Dm + Mm))
            - 0.204586 * cos(radians(2 * Dm - Ms)) * E
            - 0.129620 * cos(radians(Mm - Ms)) * E
            + 0.108743 * cos(radians(Dm))
            + 0.104755 * cos(radians(Mm + Ms)) * E
            + 0.010321 * cos(radians(2 * Dm - 2 * Fm))
            + 0.079661 * cos(radians(Mm - 2 * Fm))
            - 0.034782 * cos(radians(4 * Dm - Mm))
            - 0.023210 * cos(radians(3 * Mm))
            - 0.021636 * cos(radians(4 * Dm - 2 * Mm))
            + 0.024208 * cos(radians(2 * Dm + Ms - Mm)) * E
            + 0.030824 * cos(radians(2 * Dm + Ms)) * E
            - 0.008379 * cos(radians(Dm - Mm))
            - 0.016675 * cos(radians(Dm + Ms)) * E
            - 0.012831 * cos(radians(2 * Dm - Ms + Mm)) * E
            - 0.010445 * cos(radians(2 * Dm + 2 * Mm))
        )

        # Illumination angle IM (degrees)
        IM = (
            180
            - Dm
            - 6.289 * sin(radians(Mm))
            + 2.100 * sin(radians(Ms)) * E
            - 1.274 * sin(radians(2 * Dm - Mm))
            - 0.658 * sin(radians(2 * Dm))
            - 0.214 * sin(radians(2 * Mm))
            - 0.114 * sin(radians(Dm))
        )

        IM = IM % 360
        illumination = (1 + cos(radians(IM))) / 2 * 100

        # Distance in km
        distance = int(385000.56 + ER * 1000)

        # Trend (waxing/waning) by comparing illumination with a slightly later
        # time
        jd2 = jd + 0.5
        T2 = (jd2 - 2451545.0) / 36525.0

        Dm2 = (
            297.8501921
            + 445267.114034 * T2
            - 0.0018819 * T2 * T2
            + T2 * T2 * T2 / 545868
            - T2 * T2 * T2 * T2 / 113065000
        )

        Ms2 = (
            357.5291092
            + 35999.0502909 * T2
            - 0.0001536 * T2 * T2
            + T2 * T2 * T2 / 24490000
        )

        Mm2 = (
            134.9633964
            + 477198.8675055 * T2
            + 0.0087414 * T2 * T2
            + T2 * T2 * T2 / 69699
            - T2 * T2 * T2 * T2 / 14712000
        )

        IM2 = (180 -
               Dm2 -
               6.289 *
               sin(radians(Mm2)) +
               2.100 *
               sin(radians(Ms2)) *
               (1 -
                0.002516 *
                T2 -
                0.0000074 *
                T2 *
                T2) -
               1.274 *
               sin(radians(2 *
                           Dm2 -
                           Mm2)) -
               0.658 *
               sin(radians(2 *
                           Dm2)) -
               0.214 *
               sin(radians(2 *
                           Mm2)) -
               0.114 *
               sin(radians(Dm2)))

        IM2 = IM2 % 360
        illum2 = (1 + cos(radians(IM2))) / 2 * 100

        trend = 1 if illum2 > illumination else -1

        # --- DETERMINING PHASE NAME BASED ON AGE ---
        from datetime import datetime
        # Calculate the age in days since the last reference new moon (6 Jan
        # 2000 00:00 UTC)
        ref_jd = self._date_to_jd(datetime(2000, 1, 6, 0, 0, 0))
        days_since_ref = jd - ref_jd
        age = days_since_ref % self.SYNODIC_MONTH

        if age < 1.5:
            phase_name = "New Moon"
        elif age < 6.5:
            phase_name = "Waxing Crescent"
        elif age < 8.5:
            phase_name = "First Quarter"
        elif age < 13.5:
            phase_name = "Waxing Gibbous"
        elif age < 15.5:
            phase_name = "Full Moon"
        elif age < 20.5:
            phase_name = "Waning Gibbous"
        elif age < 22.5:
            phase_name = "Last Quarter"
        else:
            phase_name = "Waning Crescent"

        return {
            "illumination": illumination,
            "phase_name": phase_name,
            "distance": distance,
            "trend": trend,
        }

    def _get_current_phase_value(self):
        # This method is kept for compatibility but not used in precise mode
        # We'll still use it if needed, but better to use precise.
        ref_time = mktime(self.NEW_MOON_REF)
        ref_days = ref_time / 86400.0
        now_days = mktime(localtime()) / 86400.0
        days_since_ref = now_days - ref_days
        phase = (days_since_ref % self.SYNODIC_MONTH) / self.SYNODIC_MONTH
        return phase

    def _illumination_from_phase(self, phase):
        return (1 - cos(2 * pi * phase)) / 2 * 100

    def _get_phase_name(self, phase):
        # Approximate phase names
        if phase < 0.03 or phase >= 0.97:
            return "New Moon"
        elif phase < 0.22:
            return "Waxing Crescent"
        elif phase < 0.28:
            return "First Quarter"
        elif phase < 0.47:
            return "Waxing Gibbous"
        elif phase < 0.53:
            return "Full Moon"
        elif phase < 0.72:
            return "Waning Gibbous"
        elif phase < 0.78:
            return "Last Quarter"
        else:
            return "Waning Crescent"

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def get_phase_info(self):
        """
        Returns a dictionary with phase, illumination, name, icon number, and icon path.
        Gives priority to API data if available, otherwise falls back to precise internal calculation.
        """
        if self.api_data and self.api_data["illumination"] is not None and self.api_data["phase"] != "N/A":
            # Use API data
            illum_percent = self.api_data["illumination"] * 100
            phase_name = self.api_data["phase"]
            # Determine waxing/waning from phase name
            crescente = phase_name in [
                "Waxing Crescent",
                "First Quarter",
                "Waxing Gibbous"]
            # Linear mapping
            if crescente:
                icon_number = int(round(illum_percent * 50 / 100))
            else:
                icon_number = int(round(50 + (100 - illum_percent) * 50 / 100))
            if phase_name == "New Moon":
                icon_number = 0 if illum_percent < 10 else 100
            elif phase_name == "Full Moon":
                icon_number = 50
            icon_number = max(0, min(100, icon_number))
            illumination = illum_percent
            name = phase_name
            # We don't have distance from API, use precise calculation for
            # distance
            jd = self._get_julian_day()
            distance = self._compute_lunar_data(jd)['distance']
        else:
            # Fallback to precise calculation
            jd = self._get_julian_day()
            data = self._compute_lunar_data(jd)
            illumination = data['illumination']
            name = data['phase_name']
            distance = data['distance']
            # Map illumination to icon using the same logic as API case
            crescente = data['trend'] == 1
            if crescente:
                icon_number = int(round(illumination * 50 / 100))
            else:
                icon_number = int(round(50 + (100 - illumination) * 50 / 100))
            if name == "New Moon":
                icon_number = 0 if illumination < 10 else 100
            elif name == "Full Moon":
                icon_number = 50
            icon_number = max(0, min(100, icon_number))

        # Find icon file
        icon_file = None
        if self.icon_path:
            icon_file = join(self.icon_path, f"moon{icon_number:04d}.png")
            if not exists(icon_file):
                icon_file = self._find_nearest_icon(icon_number)

        return {
            "illumination": illumination,
            "name": name,
            "icon_number": icon_number,
            "icon_path": icon_file,
            "distance": distance
        }

    def _get_julian_day(self, t=None):
        if t is None:
            t = mktime(localtime())
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

    def get_phase_info_for_jd(self, jd):
        """
        Returns lunar information for a given Julian Day.
        Similar to get_phase_info() but based on the specified JD.
        """
        data = self._compute_lunar_data(jd)
        illumination = data['illumination']
        # already calculated in _compute_lunar_data
        phase_name = data['phase_name']
        distance = data['distance']
        trend = data['trend']

        # Map illumination to icon (0–100) linearly, with corrections for the main phases
        # The icon must be consistent with the phase name.
        if phase_name == "New Moon":
            icon_number = 0 if illumination < 10 else 100
        elif phase_name == "Waxing Crescent":
            # illumination from ~0 to 50% → icon from 0 to 25
            icon_number = int(round(illumination * 25 / 50))
        elif phase_name == "First Quarter":
            icon_number = 25
        elif phase_name == "Waxing Gibbous":
            # illumination from ~50 to 100% → icon from 25 to 50
            icon_number = int(round(25 + (illumination - 50) * 25 / 50))
        elif phase_name == "Full Moon":
            icon_number = 50
        elif phase_name == "Waning Gibbous":
            # illumination from 100 to 50% → icon from 50 to 75
            icon_number = int(round(50 + (100 - illumination) * 25 / 50))
        elif phase_name == "Last Quarter":
            icon_number = 75
        elif phase_name == "Waning Crescent":
            # illumination from 50 to 0% → icon from 75 to 100
            icon_number = int(round(75 + (50 - illumination) * 25 / 50))
        else:
            # fallback (should not happen)
            waxing = (trend == 1)
            if waxing:
                icon_number = int(round(illumination * 50 / 100))
            else:
                icon_number = int(round(50 + (100 - illumination) * 50 / 100))
            icon_number = max(0, min(100, icon_number))

        # Ensure the icon number stays within the 0–100 range
        icon_number = max(0, min(100, icon_number))

        icon_file = None
        if self.icon_path:
            icon_file = join(self.icon_path, f"moon{icon_number:04d}.png")
            if not exists(icon_file):
                icon_file = self._find_nearest_icon(icon_number)

        return {
            'illumination': illumination,
            'name': phase_name,
            'distance': distance,
            'icon_number': icon_number,
            'icon_path': icon_file,
            'jd': jd,
            'trend': trend
        }

    # -------------------------------------------------------------------------
    # API methods (unchanged)
    # -------------------------------------------------------------------------
    def get_moon_data_async(
            self,
            lat,
            lon,
            callback,
            max_days=2,
            offset_hours=None):
        def worker():
            result = self.get_moon_data_from_api(
                lat, lon, max_days, offset_hours)
            if callback:
                callback(result)
        Thread(target=worker).start()

    def get_moon_data_from_api(self, lat, lon, max_days=2, offset_hours=None):
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
            result = {
                "rise": moonrise,
                "set": moonset,
                "phase": phase_name,
                "illumination": illumination
            }
            if illumination is not None:
                self.api_data = result
            return result
        except Exception as e:
            print(f"[Moon] Exception: {e}")
            return None

    def _get_offset_hours(self):
        lt = time.localtime()
        if lt.tm_isdst > 0:
            offset_sec = -time.altzone
        else:
            offset_sec = -time.timezone
        return round(offset_sec / 3600.0, 1)

    def get_moon_distance(self):
        # Use precise calculation
        jd = self._get_julian_day()
        return self._compute_lunar_data(jd)['distance']

    def _find_nearest_icon(self, target_num):
        if not self.icon_path or not isdir(self.icon_path):
            return None
        pattern = join(self.icon_path, "moon*.png")
        files = glob.glob(pattern)
        numbers = []
        for f in files:
            base = basename(f)
            num_str = base.replace('moon', '').replace('.png', '')
            if num_str.isdigit():
                numbers.append((int(num_str), f))
        if not numbers:
            return None
        nearest = min(numbers, key=lambda x: abs(x[0] - target_num))
        return nearest[1]
