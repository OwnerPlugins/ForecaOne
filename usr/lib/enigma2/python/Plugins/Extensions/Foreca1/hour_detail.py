#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# hour_detail.py - Detailed view for a single hour

from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from enigma import gRGB
from skin import parseColor
from Screens.HelpMenu import HelpableScreen
from os.path import exists, join

from . import (
    _,
    PLUGIN_PATH,
    load_skin_for_class,
    apply_global_theme
)
from .google_translate import trans
from .foreca_weather_api import _symbol_to_description


class HourDetailView(Screen, HelpableScreen):
    def __init__(
            self,
            session,
            weather_api,
            foreca_preview,
            unit_manager,
            hour_data):
        """
        hour_data: dict containing all available data for the selected hour.
        """
        self.skin = load_skin_for_class(HourDetailView)
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.weather_api = weather_api
        self.foreca_preview = foreca_preview
        self.unit_manager = unit_manager
        self.hour_data = hour_data

        # Inherit colors and transparency from main screen
        self.rgbmyr = foreca_preview.rgbmyr
        self.rgbmyg = foreca_preview.rgbmyg
        self.rgbmyb = foreca_preview.rgbmyb
        self.alpha = foreca_preview.alpha

        self.setTitle(_("Hour Details"))

        # Widgets (to be defined in skin)
        self["title_location"] = Label()
        self["title_datetime"] = Label()
        self["condition_icon"] = Pixmap()
        self["condition_text"] = Label()

        self["summary"] = Label()

        self["temp_label"] = Label(_("Temperature"))
        self["temp_value"] = Label()
        self["feels_label"] = Label(_("Feels like"))
        self["feels_value"] = Label()

        self["wind_dir_label"] = Label(_("Wind direction"))
        self["wind_dir_icon"] = Pixmap()

        self["wind_speed_label"] = Label(_("Wind speed"))
        self["wind_speed_value"] = Label()

        self["precip_label"] = Label(_("Precipitation"))
        self["precip_value"] = Label()
        self["humidity_label"] = Label(_("Humidity"))
        self["humidity_value"] = Label()
        self["uvi_label"] = Label(_("UV Index"))
        self["uvi_value"] = Label()

        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("Refresh"))
        self["key_yellow"] = StaticText()
        self["key_blue"] = StaticText()

        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.close, _("Exit")),
                "red": (self.close, _("Exit")),
                "green": (self.refresh, _("Refresh")),
                # yellow and blue unassigned
            },
            -1
        )
        self.onLayoutFinish.append(self.update_display)
        self.onLayoutFinish.append(self._apply_theme)

    def _apply_theme(self):
        apply_global_theme(self)

    def refresh(self):
        # For now, just close and reopen? Or we could re-fetch data.
        # Since hour_data is static, maybe just close.
        self.update_display()

    def update_display(self):
        # Location and date/time
        location = f"{self.hour_data['town']}, {trans(self.hour_data['country'])}"
        dt = f"{self.hour_data['date']} {self.hour_data['day']} - {self.hour_data['time']}"
        self["title_location"].setText(location)
        self["title_datetime"].setText(dt)

        # Weather condition
        condition = self.hour_data['condition']
        icon_path = join(PLUGIN_PATH, "thumb", f"{condition}.png")
        if exists(icon_path):
            self["condition_icon"].instance.setPixmapFromFile(icon_path)
        else:
            fallback = join(PLUGIN_PATH, "thumb", "d000.png")
            self["condition_icon"].instance.setPixmapFromFile(fallback)
        desc = _symbol_to_description(condition)
        self["condition_text"].setText(trans(desc))

        # Temperature
        try:
            temp_val = float(self.hour_data['temp'])
            converted, unit = self.unit_manager.convert_temperature(temp_val)
            self["temp_value"].setText(f"{converted:.0f}{unit}")
        except BaseException:
            self["temp_value"].setText("N/A")

        # Feels like
        try:
            feels_val = float(self.hour_data['feels_like'])
            converted, unit = self.unit_manager.convert_temperature(feels_val)
            self["feels_value"].setText(f"{converted:.0f}{unit}")
        except BaseException:
            self["feels_value"].setText("N/A")

        # Wind direction icon
        wind_dir = self.hour_data['wind_dir']
        wind_icon_path = join(PLUGIN_PATH, "thumb", f"{wind_dir}.png")
        if exists(wind_icon_path):
            self["wind_dir_icon"].instance.setPixmapFromFile(wind_icon_path)
        else:
            fallback = join(PLUGIN_PATH, "thumb", "wN.png")
            self["wind_dir_icon"].instance.setPixmapFromFile(fallback)

        # Wind speed
        try:
            speed = float(self.hour_data['wind_speed'])
            converted, unit = self.unit_manager.convert_wind(speed)
            self["wind_speed_value"].setText(f"{converted:.1f} {unit}")
        except BaseException:
            self["wind_speed_value"].setText("N/A")

        # Precipitation (probability)
        precip = self.hour_data['precipitation']
        self["precip_value"].setText(f"{precip}%")

        # Humidity
        hum = self.hour_data['humidity']
        self["humidity_value"].setText(f"{hum}%")

        # UV Index
        uvi = self.hour_data['uvi']
        self["uvi_value"].setText(str(uvi))

        summary = self._format_summary()
        self["summary"].setText(summary)

        # Background colors
        bg = gRGB(int(self.rgbmyr), int(self.rgbmyg), int(self.rgbmyb))
        self["background_plate"].instance.setBackgroundColor(bg)
        self["selection_overlay"].instance.setBackgroundColor(
            parseColor(self.alpha))

    def _format_summary(self):
        data = self.hour_data
        desc = _symbol_to_description(data['condition'])
        desc_trans = trans(desc)
        try:
            temp_val, temp_unit = self.unit_manager.convert_temperature(
                float(data['temp']))
            feels_val, _dummy = self.unit_manager.convert_temperature(
                float(data['feels_like']))
            wind_val, wind_unit = self.unit_manager.convert_wind(
                float(data['wind_speed']))
        except Exception as e:
            print(f"[HourDetail] Conversion error: {e}")
            temp_val = feels_val = wind_val = 0
            temp_unit = wind_unit = ""

        summary = f"{desc_trans}. {_('Temp')}: {temp_val:.0f}{temp_unit}, {_('Feels like')}: {feels_val:.0f}{temp_unit}. "
        summary += f"{_('Wind')}: {wind_val:.1f} {wind_unit} {data['wind_dir']}. "
        summary += f"{_('Precip')}: {data['precipitation']}%, {_('Humidity')}: {data['humidity']}%, {_('UV')}: {data['uvi']}."
        return summary
