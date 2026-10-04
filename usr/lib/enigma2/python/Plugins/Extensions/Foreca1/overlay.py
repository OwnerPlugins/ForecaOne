#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# overlay.py - Small temperature overlay on top of TV

from os.path import exists, join
from enigma import eTimer, getDesktop
from Screens.Screen import Screen
from Components.Label import Label

from . import SYSTEM_DIR, DEBUG

OVERLAY_ENABLED_FILE = join(SYSTEM_DIR, "overlay_enabled.cfg")
OVERLAY_TEMP_FILE = join(SYSTEM_DIR, "overlay_temp.txt")

_overlay_screen = None
_overlay_session = None


def is_enabled():
    """True if the user turned the overlay on."""
    if not exists(OVERLAY_ENABLED_FILE):
        return False
    try:
        with open(OVERLAY_ENABLED_FILE, "r") as f:
            return f.read().strip() == "1"
    except Exception:
        return False


def set_enabled(value):
    """Persist the on/off state to disk."""
    try:
        with open(OVERLAY_ENABLED_FILE, "w") as f:
            f.write("1" if value else "0")
    except Exception as e:
        if DEBUG:
            print(f"[Foreca1] overlay state write error: {e}")
    refresh()


def _read_temp():
    if not exists(OVERLAY_TEMP_FILE):
        return None
    try:
        with open(OVERLAY_TEMP_FILE, "r") as f:
            content = f.read().strip()
        return content or None
    except Exception:
        return None


def write_temperature(text):
    """Called by the main screen after each weather refresh."""
    try:
        with open(OVERLAY_TEMP_FILE, "w") as f:
            f.write(str(text))
    except Exception as e:
        if DEBUG:
            print(f"[Foreca1] overlay temp write error: {e}")


def refresh():
    """Force an immediate overlay redraw (called after toggle or update)."""
    global _overlay_screen
    if _overlay_screen is not None:
        try:
            _overlay_screen._refresh()
        except Exception:
            pass


class TempOverlay(Screen):
    """Small always-on-top overlay showing the current temperature."""

    def __init__(self, session):
        cur_w = getDesktop(0).size().width()
        ov_w = 130 if cur_w > 1800 else 110
        ov_h = 44 if cur_w > 1800 else 38

        self.skin = f"""
        <screen name="TempOverlay"
                position="{cur_w - ov_w - 15},15"
                size="{ov_w},{ov_h}"
                flags="wfNoBorder"
                backgroundColor="transparent">
            <widget name="overlay_temp"
                    position="0,0"
                    size="{ov_w},{ov_h}"
                    valign="center"
                    halign="center"
                    zPosition="1"
                    font="Regular;28"
                    foregroundColor="#00ffd700"
                    backgroundColor="#40000000"
                    transparent="0"
                    shadowColor="black"
                    shadowOffset="-2,-2"/>
        </screen>
        """
        Screen.__init__(self, session)
        self["overlay_temp"] = Label("")
        self._timer = eTimer()
        self._timer.callback.append(self._refresh)
        # Defer the first show/hide until Enigma2 has fully attached
        # the dialog to the GUI layer. Calling _refresh() directly in
        # __init__ is too early at session start: the widget is created
        # but show() has no effect, so the overlay stays hidden even
        # when the enabled file contains "1".
        self._init_timer = eTimer()
        self._init_timer.callback.append(self._initial_refresh)
        self._init_timer.start(2500, True)  # 2.5 s, one shot
        self._timer.start(60000)

    def _initial_refresh(self):
        self._refresh()

    def _refresh(self):
        text = _read_temp()
        self["overlay_temp"].setText(text if text else "--")
        if is_enabled():
            self.show()
        else:
            self.hide()


def autostart(reason, **kwargs):
    """Called by Enigma2 at session start / end."""
    global _overlay_screen, _overlay_session

    if reason != 0:
        return

    session = kwargs.get("session")
    if session is None:
        if DEBUG:
            print("[Foreca1] overlay autostart: no session")
        return

    _overlay_session = session
    try:
        _overlay_screen = session.instantiateDialog(TempOverlay)
        if DEBUG:
            print("[Foreca1] overlay instantiated")
    except Exception as e:
        if DEBUG:
            print(f"[Foreca1] overlay autostart error: {e}")
