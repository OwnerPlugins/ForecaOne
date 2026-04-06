#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# moon_calendar.py - Annual lunar phase calendar

from datetime import datetime, timedelta
from os.path import exists, join
from collections import defaultdict
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
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
        self["Phase"] = Label(_("Phase"))
        self["Day"] = Label(_("Day"))
        self["Month"] = Label(_("Month"))
        self["Time"] = Label(_("Time"))

        self["current_phase_icon"] = Pixmap()
        self["current_phase_name"] = Label()
        self["current_illum"] = Label()
        self["current_distance"] = Label()
        self["illum_bar"] = ProgressBar()

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

    # -------------------------------------------------------------------------
    # Helper methods for special events
    # -------------------------------------------------------------------------

    def _is_supermoon(self, full_moon):
        """Return True if the full moon is a supermoon (distance = 360000 km)."""
        return full_moon.get('distance', 999999) <= 360000

    def _get_blue_moons(self, full_moons):
        """Return list of blue moons (second full moon in a calendar month)."""
        by_month = defaultdict(list)
        for fm in full_moons:
            key = (fm['date'].year, fm['date'].month)
            by_month[key].append(fm)

        blue = []

        for month, fms in by_month.items():
            if len(fms) == 2:
                blue.append(fms[1])  # second is the blue moon

        return blue

    def _get_black_moons(self, new_moons):
        """Return list of black moons (second new moon in a calendar month)."""
        by_month = defaultdict(list)
        for nm in new_moons:
            key = (nm['date'].year, nm['date'].month)
            by_month[key].append(nm)

        black = []
        for month, nms in by_month.items():
            if len(nms) == 2:
                black.append(nms[1])

        return black

    def _get_perigee_for_month(self, year, month):
        """Find the perigee (minimum lunar distance) within the given month.

        Returns:
            dict | None: A dictionary containing date, distance, icon_path,
            and phase_name, or None if no perigee was found.
        """
        from datetime import datetime, timedelta

        start = datetime(year, month, 1)

        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)

        jd_start = self.moon._date_to_jd(start)
        jd_end = self.moon._date_to_jd(end)

        best_jd = None
        best_dist = float("inf")

        jd = jd_start
        while jd <= jd_end:
            data = self.moon._compute_lunar_data(jd)

            if data["distance"] < best_dist:
                best_dist = data["distance"]
                best_jd = jd

            jd += 1

        if best_jd:
            dt = self.moon._jd_to_date(best_jd)
            info = self.moon.get_phase_info_for_jd(
                best_jd)   # ottiene tutti i dati
            return {
                'date': dt,
                'distance': best_dist,
                'icon_path': info['icon_path'],
                'phase_name': info['name'],          # real phase of the day
                'illumination': info['illumination'],
                'event_type': 'Perigee'
            }
        return None

    # -------------------------------------------------------------------------
    # Calendar generation
    # -------------------------------------------------------------------------

    def load_calendar(self):
        """Generate the list of lunar phases and special events for the next 12 months."""
        self["info"].setText(_("Calculating..."))
        self.phases = []
        today = datetime.now()
        # Start from the first day of next month
        if today.month == 12:
            start_month = 1
            start_year = today.year + 1
        else:
            start_month = today.month  # + 1
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

        # --- Collect full moons and new moons from self.phases ---
        full_moons = [p for p in self.phases if p["phase_name"] == "Full Moon"]
        new_moons = [p for p in self.phases if p["phase_name"] == "New Moon"]

        # 1) Supermoons
        supermoons = [fm for fm in full_moons if self._is_supermoon(fm)]

        # 2) Blue moons
        blue_moons = self._get_blue_moons(full_moons)

        # 3) Black moons
        black_moons = self._get_black_moons(new_moons)

        # 4) Perigees for each month
        perigees = []
        for year, month in {(p["date"].year, p["date"].month)
                            for p in self.phases}:
            perigee_data = self._get_perigee_for_month(year, month)
            if perigee_data:
                perigees.append(perigee_data)

        # Add special events as new entries (copy to avoid altering original
        # phases)
        special_events = []

        for sm in supermoons:
            # Add a modified copy so the original entry is not altered
            ev = sm.copy()
            ev["event_type"] = "Supermoon"
            ev["phase_name"] = "Supermoon"
            special_events.append(ev)

        for bm in blue_moons:
            ev = bm.copy()
            ev["event_type"] = "Blue Moon"
            ev["phase_name"] = "Blue Moon"
            special_events.append(ev)

        for bkm in black_moons:
            ev = bkm.copy()
            ev["event_type"] = "Black Moon"
            ev["phase_name"] = "Black Moon"
            special_events.append(ev)

        for pg in perigees:
            special_events.append(pg)

        # Merge all events and sort by date
        self.phases.extend(special_events)
        self.phases.sort(key=lambda x: x["date"])

        # Build the list for the Listbox
        self.list = []
        # self.list.append((
        # _("Month"),        # 0
        # None,              # 1: no icon
        # _("Phase"),        # 2
        # _("Day"),          # 3
        # _("Time")          # 4
        # ))
        for p in self.phases:
            self.list.append(self._create_entry(p))
        # Update current moon info
        info = self.moon.get_phase_info()

        if info["icon_path"] and exists(info["icon_path"]):
            self["current_phase_icon"].instance.setPixmapFromFile(
                info["icon_path"])
        self["current_phase_name"].setText(_(info["name"]))
        self["current_illum"].setText(
            _("Illumination: {:.1f}%").format(
                info["illumination"]))
        self["current_distance"].setText(
            _("Distance: {} km").format(
                info["distance"]))
        self["illum_bar"].setValue(int(info["illumination"]))

        self["menu"].setList(self.list)
        self["info"].setText(
            trans("Found {} lunar phases").format(len(self.phases))
        )

    def _create_entry(self, phase):
        """Create a UI entry tuple for a lunar phase or special event."""
        from os.path import join, exists

        icon_path = phase.get("icon_path")
        event_type = phase.get("event_type")

        # For perigees, use a dedicated icon if available,
        # otherwise keep the phase icon.
        if event_type == "Perigee":
            custom_icon = join(self.moon.icon_path, "perigee.png")
            if exists(custom_icon):
                icon_path = custom_icon

        if icon_path and exists(icon_path):
            icon = LoadPixmap(cached=True, path=icon_path)
        else:
            icon = None

        date = phase["date"]
        month = date.strftime("%B %Y")
        day = date.strftime("%d")
        hour = date.strftime("%H:%M")

        if event_type == "Supermoon":
            phase_text = _("Super Full Moon") + " ★"
        elif event_type == "Blue Moon":
            phase_text = _("Blue Moon") + " ☆"
        elif event_type == "Black Moon":
            phase_text = _("Black Moon") + " ◇"
        elif event_type == 'Perigee':
            phase_text = _("Perigee") + f" ({phase['distance']:.0f} km)"
        else:
            phase_text = _(phase["phase_name"])

        return (month, icon, phase_text, day, hour)

    def _get_month_phases(self, year, month):
        """Return list of the 4 main phases (new, first, full, last) for the given month."""
        # This method should already exist in your file; it's the same as before.
        # I'll just include a placeholder; you can keep your existing implementation.
        # Make sure it returns dictionaries with keys: 'date', 'phase_name', 'icon_path', 'distance', etc.
        # Example:
        target_phases = [0.0, 0.25, 0.5, 0.75]
        names = {
            0.0: "New Moon",
            0.25: "First Quarter",
            0.5: "Full Moon",
            0.75: "Last Quarter"
        }

        # Start and end of the month in Julian Day
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = datetime(year, month + 1, 1) - timedelta(days=1)

        jd_start = self.moon._date_to_jd(start_of_month)
        jd_end = self.moon._date_to_jd(end_of_month)
        jd_ref = self.moon._date_to_jd(datetime(2000, 1, 6, 0, 0, 0))
        month_phases = []
        for target in target_phases:
            jd_phase = self._find_next_phase_after(jd_start, target, jd_ref)
            while jd_phase <= jd_end:
                dt_phase = self.moon._jd_to_date(jd_phase)
                if dt_phase.year == year and dt_phase.month == month:
                    info = self.moon.get_phase_info_for_jd(jd_phase)
                    month_phases.append({
                        'date': dt_phase,
                        'phase_name': names[target],
                        'icon_path': info['icon_path'],
                        'jd': jd_phase,
                        'illumination': info['illumination'],
                        'distance': info['distance']
                    })
                # Move to the next phase (using the constant from the moon
                # object)
                jd_phase += self.moon.SYNODIC_MONTH

        month_phases.sort(key=lambda x: x['date'])
        return month_phases

    def _find_next_phase_after(self, jd_start, target_phase, jd_ref):
        """Find the Julian Day of the next target phase after jd_start."""
        days_since_ref = jd_start - jd_ref
        phase_at_start = (days_since_ref / self.moon.SYNODIC_MONTH) % 1.0
        delta = (target_phase - phase_at_start) % 1.0
        if delta < 0.0001:
            delta = 1.0
        jd_target = jd_start + delta * self.moon.SYNODIC_MONTH
        return jd_target

    def show_details(self):
        idx = self["menu"].getSelectedIndex()
        if idx < 0 or idx >= len(self.phases):
            return
        phase = self.phases[idx]
        if phase.get('event_type'):
            phase_name = _(phase['phase_name'])
        else:
            phase_name = _(phase['phase_name'])
        details = trans("Phase: {}").format(phase_name) + "\n"
        details += trans("Date: {}").format(
            phase['date'].strftime("%d.%m.%Y")) + "\n"
        details += trans("Time: {}").format(
            phase['date'].strftime("%H:%M")) + "\n"
        details += trans("Illumination: {:.1f}%").format(
            phase['illumination']) + "\n"
        details += trans("Distance: {} km").format(phase['distance'])
        self.session.open(MessageBox, details, MessageBox.TYPE_INFO)

    def exit(self):
        self.close()
