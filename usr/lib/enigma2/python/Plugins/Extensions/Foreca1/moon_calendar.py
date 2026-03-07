#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# moon_calendar.py - Annual lunar phase calendar

from datetime import datetime
from os.path import join
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap

from . import _, PLUGIN_PATH, load_skin_for_class, apply_global_theme
from .MoonPhase import MoonPhase
from .google_translate import trans


class MoonCalendar(Screen, HelpableScreen):
    def __init__(self, session, moon_obj=None):
        self.skin = load_skin_for_class(MoonCalendar)
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.setTitle(_("Lunar Calendar"))
        self.moon = moon_obj or MoonPhase(
            icon_path=join(PLUGIN_PATH, "moon"),
            total_icons=101
        )
        self.phases = []
        self.list = []
        self["menu"] = List(self.list)
        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")
        self["info"] = Label(_("Loading lunar phases..."))
        self["title"] = Label(_("Lunar phases from next month"))
        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.close, _("Exit")),
                "ok": (self.show_details, _("Details")),
                "up": (self["menu"].up, _("Move up")),
                "down": (self["menu"].down, _("Move down")),
                "pageUp": (self["menu"].pageUp, _("Page up")),
                "pageDown": (self["menu"].pageDown, _("Page down")),
            },
            -1
        )

        self.onLayoutFinish.append(self._apply_theme)
        self.onLayoutFinish.append(self.load_calendar)

    def _apply_theme(self):
        apply_global_theme(self)

    def load_calendar(self):
        """Generate the list of lunar phases for the next 12 months."""
        self["info"].setText(_("Calculating..."))
        self.phases = []
        today = datetime.now()
        # Start from the first day of next month
        if today.month == 12:
            start_month = 1
            start_year = today.year + 1
        else:
            start_month = today.month + 1
            start_year = today.year

        current = datetime(start_year, start_month, 1)

        # Calculate for 12 months
        for x in range(12):
            month_phases = self._get_month_phases(current.year, current.month)
            self.phases.extend(month_phases)
            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        # Build the list for the Listbox
        self.list = []
        self.list.append((
            trans("Month"),        # 0
            None,                  # 1: no icon
            trans("Phase"),        # 2
            trans("Day"),          # 3
            trans("Time")          # 4
        ))
        for p in self.phases:
            self.list.append(self._create_entry(p))
        self["menu"].setList(self.list)
        self["info"].setText(trans("Found {} lunar phases").format(len(self.phases)))

    def _get_month_phases(self, year, month):
        """
        Return a list of dictionaries for the 4 main phases of the month.
        """
        # Reference date: January 6, 2000 00:00 UTC (known new moon)
        ref_date = datetime(2000, 1, 6, 0, 0, 0)
        jd_ref = self._date_to_jd(ref_date)

        start_of_month = datetime(year, month, 1)
        jd_start = self._date_to_jd(start_of_month)

        target_phases = [0.0, 0.25, 0.5, 0.75]
        names = {
            0.0: _("New Moon"),
            0.25: _("First Quarter"),
            0.5: _("Full Moon"),
            0.75: _("Last Quarter")
        }

        month_phases = []
        for phase_target in target_phases:
            jd_phase = self._find_next_phase_after(jd_start, phase_target, jd_ref)
            dt = self._jd_to_date(jd_phase)
            # If the date is still in the same month, add it
            if dt.year == year and dt.month == month:
                info = self.moon.get_phase_info_for_jd(jd_phase)
                month_phases.append({
                    'date': dt,
                    'phase_name': names[phase_target],
                    'icon_path': info['icon_path'],
                    'jd': jd_phase,
                    'illumination': info['illumination'],
                    'distance': info['distance']
                })
        month_phases.sort(key=lambda x: x['date'])
        return month_phases

    def _find_next_phase_after(self, jd_start, target_phase, jd_ref):
        """Find the Julian Day of the next target phase."""
        days_since_ref = jd_start - jd_ref
        phase_at_start = (days_since_ref / 29.530588853) % 1.0
        delta = (target_phase - phase_at_start) % 1.0
        if delta < 0:
            delta += 1.0
        if delta < 0.0001:  # if already at the phase, take the next one
            delta = 1.0
        jd_target = jd_start + delta * 29.530588853
        return jd_target

    def _date_to_jd(self, dt):
        """Convert datetime to Julian Day (approximate)."""
        return dt.toordinal() + 1721424.5

    def _jd_to_date(self, jd):
        """Convert Julian Day to datetime (inverse formula)."""
        jd = jd + 0.5
        Z = int(jd)
        F = jd - Z
        if Z < 2299161:
            A = Z
        else:
            alpha = int((Z - 1867216.25) / 36524.25)
            A = Z + 1 + alpha - int(alpha / 4)
        B = A + 1524
        C = int((B - 122.1) / 365.25)
        D = int(365.25 * C)
        E = int((B - D) / 30.6001)

        day = int(B - D - int(30.6001 * E) + F)
        month = int(E - 1 if E < 14 else E - 13)
        year = int(C - 4716 if month > 2 else C - 4715)

        # Calculate hours, minutes, seconds from fractional part
        total_seconds = int(F * 86400)
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600

        return datetime(year, month, day, hours, minutes, seconds)

    def _create_entry(self, phase):
        """Create a tuple for the MultiContent template (5 elements)."""
        icon = LoadPixmap(cached=True, path=phase['icon_path'])
        date = phase['date']
        month = date.strftime("%B %Y")
        day = date.strftime("%d")
        hour = date.strftime("%H:%M")
        return (
            month,
            icon,
            phase['phase_name'],
            day,
            hour
        )

    def show_details(self):
        idx = self["menu"].getCurrentIndex()
        if idx <= 0 or idx > len(self.phases):
            return
        phase = self.phases[idx - 1]
        details = trans("Phase: {}").format(phase['phase_name']) + "\n"
        details += trans("Date: {}").format(phase['date'].strftime("%d/%m/%Y")) + "\n"
        details += trans("Time: {}").format(phase['date'].strftime("%H:%M")) + "\n"
        details += trans("Illumination: {:.1f}%").format(phase['illumination']) + "\n"
        details += trans("Distance: {} km").format(phase['distance'])
        self.session.open(MessageBox, details, MessageBox.TYPE_INFO)

    def exit(self):
        self.close()
