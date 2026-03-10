#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# map_legend.py - Color legend screen for weather maps

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from enigma import gRGB
from Components.Sources.StaticText import StaticText

from . import _, load_skin_for_class, apply_global_theme


class MapLegend(Screen, HelpableScreen):
    def __init__(self, session, layer_type="precip", overlay=False):
        self.overlay = overlay
        if overlay:
            self.skin = load_skin_for_class(MapLegendOverlay)
        else:
            self.skin = load_skin_for_class(MapLegend)

        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.setTitle(_("Color Legend"))
        self.layer_type = layer_type.lower()
        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")
        self["key_red"] = StaticText(_("Close"))
        self["title"] = Label(_("Color Legend"))
        for i in range(1, 8):
            self[f"color{i}"] = Label("")
            self[f"desc{i}"] = Label("")
        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.close, _("Exit")),
                "ok": (self.close, _("Close")),
                "red": (self.close, _("Exit")),
            },
            -1
        )

        self.onLayoutFinish.append(self._apply_theme)
        self.onLayoutFinish.append(self.populate_legend)

    def _apply_theme(self):
        apply_global_theme(self)

    def populate_legend(self):
        print("[MapLegend] populate_legend called")
        for i in range(1, 8):
            self[f"color{i}"].hide()
            self[f"desc{i}"].hide()

        if self.layer_type in ("precip", "rain", "radar"):
            legend = [
                (0x0000ff, _("Light rain / drizzle")),
                (0x00aaff, _("Light to moderate")),
                (0x00ff00, _("Moderate rain")),
                (0xffff00, _("Heavy rain")),
                (0xffaa00, _("Very heavy rain")),
                (0xff0000, _("Extreme / thunderstorms")),
                (0xcccccc, _("Snow / ice")),
            ]
        elif self.layer_type in ("temp", "temperature"):
            legend = [
                (0x0000ff, _("Cold (< 0°C)")),
                (0x00aaff, _("Cool (0-10°C)")),
                (0x00ff00, _("Mild (10-20°C)")),
                (0xffff00, _("Warm (20-30°C)")),
                (0xffaa00, _("Hot (30-40°C)")),
                (0xff0000, _("Very hot (>40°C)")),
                (0xcccccc, _("Ice / frost")),
            ]
        elif self.layer_type == "wind":
            legend = [
                (0x00ff00, _("Light (0-20 km/h)")),
                (0xffff00, _("Moderate (20-40 km/h)")),
                (0xffaa00, _("Strong (40-60 km/h)")),
                (0xff0000, _("Gale force (>60 km/h)")),
            ]
        else:
            legend = [
                (0xffffff, _("No specific legend available.")),
            ]

        for i, (color, desc) in enumerate(legend, start=1):
            if i > 7:
                break
            self[f"desc{i}"].setText(desc)
            if self[f"color{i}"].instance:
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                print(f"[MapLegend] Setting color{i} to RGB({r},{g},{b})")
                self[f"color{i}"].instance.setBackgroundColor(gRGB(r, g, b))
                self[f"color{i}"].instance.setTransparent(False)
                self[f"color{i}"].instance.invalidate()
            else:
                print(f"[MapLegend] WARNING: color{i}.instance is None")
            self[f"color{i}"].show()
            self[f"desc{i}"].show()

        for i in range(len(legend) + 1, 8):
            self[f"color{i}"].hide()
            self[f"desc{i}"].hide()


class MapLegendOverlay(MapLegend):
    def __init__(self, session, layer_type="precip", mode='text', image_path=None):
        self.mode = mode
        self.image_path = image_path
        # Choose the skin based on the mode
        if mode == 'image':
            self.skin = load_skin_for_class(MapLegendOverlayImage)
        else:
            self.skin = load_skin_for_class(MapLegendOverlay)
        MapLegend.__init__(self, session, layer_type, overlay=True)

    def populate_legend(self):
        if self.mode == 'image' and self.image_path:
            # Hide all color row widgets
            for i in range(1, 8):
                if f"color{i}" in self:
                    self[f"color{i}"].hide()
                if f"desc{i}" in self:
                    self[f"desc{i}"].hide()
            # Show Image
            if "legend_image" in self and self["legend_image"].instance:
                self["legend_image"].instance.setPixmapFromFile(self.image_path)
                self["legend_image"].show()
        else:
            # Normal behavior (textual)
            super().populate_legend()


class MapLegendOverlayImage:
    pass


"""
# class MapLegendOverlay(MapLegend):
    # def __init__(self, session, layer_type="precip"):
        # MapLegend.__init__(self, session, layer_type, overlay=True)
        # self.legend_image = None

    # def set_legend_image(self, image_path):
        # for i in range(1, 8):
            # if hasattr(self, f"color{i}"):
                # self[f"color{i}"].hide()
            # if hasattr(self, f"desc{i}"):
                # self[f"desc{i}"].hide()
        # if hasattr(self, "legend_image"):
            # self["legend_image"].instance.setPixmapFromFile(image_path)
            # self["legend_image"].show()
        # else:
            # pass

    # def show(self):
        # if hasattr(self, "legend_image") and self["legend_image"].instance:
            # self["legend_image"].show()
        # else:
            # for i in range(1, 8):
                # self[f"color{i}"].show()
                # self[f"desc{i}"].show()
        # Screen.show(self)

    # def hide(self):
        # Screen.hide(self)
"""
