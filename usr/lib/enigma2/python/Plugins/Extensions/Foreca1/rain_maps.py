#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# wetter_maps.py - RainViewer radar viewer with geographic background
# (free, no API key)

import requests
from datetime import datetime
from threading import Thread
from os.path import exists, join
from os import makedirs
from math import log, tan, pi, radians, cos

from enigma import getDesktop
from twisted.internet import reactor

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from PIL import Image

from .google_translate import trans
from . import (
    _,
    # DEBUG,
    load_skin_for_class,
    apply_global_theme,
    THUMB_PATH,
    TEMP_DIR,
    HEADERS
)


RAIN_MAPS_DIR = join(TEMP_DIR, "rainviewer")
if not exists(RAIN_MAPS_DIR):
    makedirs(RAIN_MAPS_DIR)

TILE_SIZE = 256
API_URL = "https://api.rainviewer.com/public/weather-maps.json"
OSM_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"


BACKGROUND_EXTENTS = {
    # Europe (based on get_background_for_layer)
    'europa.png': {'minLat': 36, 'maxLat': 71, 'minLon': -9.57, 'maxLon': 66.17},
    # Africa
    'africa.png': {'minLat': -34.85, 'maxLat': 37.35, 'minLon': -17.56, 'maxLon': 51.46},
    # Asia (two ranges to cross 180°)
    'asia.png': {'minLat': -1.27, 'maxLat': 77.72, 'minLon': 26.07, 'maxLon': 180},
    # North America (two ranges)
    'nordamerika.png': {'minLat': 7.2, 'maxLat': 83.67, 'minLon': -180, 'maxLon': -12.13},
    # South America
    'suedamerika.png': {'minLat': -56.5, 'maxLat': 12.45, 'minLon': -81.33, 'maxLon': -34.78},
    # Oceania
    'oceania.png': {'minLat': -55.05, 'maxLat': 28.63, 'minLon': 110, 'maxLon': 180},
    # World (fallback)
    'world.png': {'minLat': -90, 'maxLat': 90, 'minLon': -180, 'maxLon': 180},
}


class RainViewerMaps(Screen, HelpableScreen):
    def __init__(self, session, foreca_preview):
        self.skin = load_skin_for_class(RainViewerMaps)
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.setTitle(_("RainViewer Radar"))

        self.foreca_preview = foreca_preview
        self.host = None
        self.frames = []
        self.current_frame = 0

        try:
            self.center_lat = float(
                foreca_preview.lat) if foreca_preview.lat != 'N/A' else 50.0
            self.center_lon = float(
                foreca_preview.lon) if foreca_preview.lon != 'N/A' else 10.0
        except BaseException:
            self.center_lat = 50.0
            self.center_lon = 10.0
        self.zoom_level = 5
        self.min_zoom = 2
        self.max_zoom = 7

        desktop = getDesktop(0)
        self.screen_w = desktop.size().width()
        self.screen_h = desktop.size().height()
        if self.screen_h <= 720:
            self.grid_cols = 5
            self.grid_rows = 3
        elif self.screen_h <= 1080:
            self.grid_cols = 5
            self.grid_rows = 5
        else:
            self.grid_cols = 7
            self.grid_rows = 7

        self.map_w = self.grid_cols * TILE_SIZE
        self.map_h = self.grid_rows * TILE_SIZE

        # Widgets
        self["map"] = Pixmap()
        self["title"] = Label(_("RainViewer Radar"))
        self["time_label"] = Label("")
        self["info"] = Label(_("Loading..."))
        self['key_red'] = StaticText(_("Exit"))
        self['key_green'] = StaticText(_("Zoom+"))
        self['key_yellow'] = StaticText(_("Zoom-"))
        self['key_blue'] = StaticText()
        self['key_left'] = StaticText(_("← Frame"))
        self['key_right'] = StaticText(_("Frame →"))
        self['zoom_label'] = Label(_("Zoom: ") + str(self.zoom_level))

        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")
        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.exit, _("Exit")),
                "red": (self.exit, _("Exit")),
                "green": (self.zoom_in, _("Zoom+")),
                "yellow": (self.zoom_out, _("Zoom-")),
                "left": (self.pan_left, _("Left")),
                "right": (self.pan_right, _("Right")),
                "up": (self.pan_up, _("Up")),
                "down": (self.pan_down, _("Down")),
                "pageUp": (self.prev_frame, _("Previous frame")),
                "pageDown": (self.next_frame, _("Next frame")),
            },
            -1
        )
        self.onLayoutFinish.append(self._apply_theme)
        self.onLayoutFinish.append(self.load_frame_list)

    def _apply_theme(self):
        apply_global_theme(self)

    def load_frame_list(self):
        """Download the JSON and get the list of available frames"""
        self["info"].setText(trans("Fetching radar data..."))
        Thread(target=self._fetch_frames).start()

    def _fetch_frames(self):
        try:
            resp = requests.get(API_URL, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"[RainViewer] API error: {resp.status_code}")
                reactor.callFromThread(
                    lambda: self["info"].setText(
                        _("API error")))
                return
            data = resp.json()
            self.host = data['host']
            self.frames = [frame['path'] for frame in data['radar']['past']]
            self.frames.reverse()  # oldest to newest
            self.current_frame = len(self.frames) - 1  # last frame
            print(
                f"[RainViewer] {len(self.frames)} frames available, host: {self.host}")
            reactor.callFromThread(self.update_frame_display)
        except Exception as e:
            print(f"[RainViewer] Error: {e}")
            reactor.callFromThread(
                lambda: self["info"].setText(
                    _("Error loading data")))

    def update_frame_display(self):
        if not self.frames:
            return
        frame_path = self.frames[self.current_frame]
        timestamp = frame_path.split('/')[-1]  # extract the number
        try:
            dt = datetime.utcfromtimestamp(int(timestamp))
            time_str = dt.strftime("%d/%m %H:%M UTC")
        except BaseException:
            time_str = timestamp
        self["time_label"].setText(_("Frame: {}").format(time_str))
        self["info"].setText(trans("Loading tiles..."))
        print(f"[RainViewer] Loading frame: {frame_path}")
        self.download_tiles(frame_path)

    def download_tiles(self, frame_path):
        """Download and compose tiles for the selected frame"""
        Thread(target=self._download_thread, args=(frame_path,)).start()

    def _download_thread(self, frame_path):
        cx, cy = self.latlon_to_tile(
            self.center_lat, self.center_lon, self.zoom_level)
        offset_cols = self.grid_cols // 2
        offset_rows = self.grid_rows // 2

        osm_tiles = []
        radar_tiles = []
        for dx in range(-offset_cols, offset_cols + 1):
            for dy in range(-offset_rows, offset_rows + 1):
                x = cx + dx
                y = cy + dy
                # OSM tile
                osm_url = OSM_URL.format(z=self.zoom_level, x=x, y=y)
                osm_path = self.download_tile(osm_url, prefix='osm')
                if osm_path:
                    osm_tiles.append(
                        (dx + offset_cols, dy + offset_rows, osm_path))
                # Radar tile
                radar_url = self.build_tile_url(
                    frame_path, x, y, self.zoom_level)
                radar_path = self.download_tile(radar_url, prefix='radar')
                if radar_path:
                    radar_tiles.append(
                        (dx + offset_cols, dy + offset_rows, radar_path))

        if osm_tiles and radar_tiles:
            merged = self.merge_tiles(osm_tiles, radar_tiles)
            if merged:
                reactor.callFromThread(self.show_map, merged)
        else:
            reactor.callFromThread(
                lambda: self["info"].setText(
                    _("No tiles downloaded")))

    def build_tile_url(self, frame_path, x, y, z):
        # Fixed parameters: size=256, color=2 (green-red), options=1_1 (blur +
        # snow)
        return f"{self.host}{frame_path}/256/{z}/{x}/{y}/2/1_1.png"

    def download_tile(self, url, prefix=''):
        import hashlib
        key = (prefix + url).encode()
        cache_file = join(RAIN_MAPS_DIR, hashlib.md5(key).hexdigest() + '.png')
        if exists(cache_file):
            return cache_file
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                with open(cache_file, 'wb') as f:
                    f.write(r.content)
                return cache_file
            else:
                print(
                    f"[RainViewer] Tile download error {r.status_code}: {url}")
        except Exception as e:
            print(f"[RainViewer] download exception: {e}")
        return None

    def merge_tiles(self, osm_tiles, radar_tiles):
        """First merge the OSM tiles (background) and then overlay the radar tiles."""
        try:
            # Create background with OSM tiles
            bg = Image.new('RGBA', (self.map_w, self.map_h), (0, 0, 0, 255))
            for col, row, path in osm_tiles:
                tile = Image.open(path).convert('RGBA')
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                bg.paste(tile, (x, y), tile)

            # Overlay radar tiles
            for col, row, path in radar_tiles:
                tile = Image.open(path).convert('RGBA')
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                bg.paste(tile, (x, y), tile)

            bg_rgb = bg.convert('RGB')
            out_path = join(RAIN_MAPS_DIR, 'merged.jpg')
            bg_rgb.save(out_path, 'JPEG', quality=90)
            return out_path
        except Exception as e:
            print(f"[RainViewer] merge error: {e}")
            return None

    def show_map(self, path):
        from PIL import Image
        img = Image.open(path)
        # Get widget dimensions
        widget_width = self["map"].instance.size().width()
        widget_height = self["map"].instance.size().height()
        # Resize to fit widget (possibly fill)
        img_resized = img.resize(
            (widget_width, widget_height), Image.Resampling.LANCZOS)
        # resized_path = path.replace('.png', '_widget.png')
        resized_path = path.replace('.jpg', '_widget.jpg')
        img_resized.save(resized_path)
        self["map"].instance.setPixmapFromFile(resized_path)
        self["map"].instance.show()
        self["info"].setText(trans("Map loaded"))

    def latlon_to_tile(self, lat, lon, zoom):
        lat_rad = radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - log(tan(lat_rad) + 1.0 / cos(lat_rad)) / pi) / 2.0 * n)
        return x, y

    def zoom_in(self):
        if self.zoom_level < self.max_zoom:
            self.zoom_level += 1
            self['zoom_label'].setText(_("Zoom: ") + str(self.zoom_level))
            self.update_frame_display()

    def zoom_out(self):
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= 1
            self['zoom_label'].setText(_("Zoom: ") + str(self.zoom_level))
            self.update_frame_display()

    def prev_frame(self):
        if self.current_frame > 0:
            self.current_frame -= 1
            self.update_frame_display()

    def next_frame(self):
        if self.current_frame < len(self.frames) - 1:
            self.current_frame += 1
            self.update_frame_display()

    """
    def pan_left(self):
        self.center_lon -= 0.5
        self.update_frame_display()

    def pan_right(self):
        self.center_lon += 0.5
        self.update_frame_display()

    def pan_up(self):
        self.center_lat += 0.5
        self.update_frame_display()

    def pan_down(self):
        self.center_lat -= 0.5
        self.update_frame_display()
    """

    """
    Adjust the base step
    The 0.5 value in the formula is empirical.
    You can adjust it to achieve the desired sensitivity.
    If you want the movement to be faster, increase the value;
    if you want it to be slower, decrease it.
    """

    def pan_left(self):
        step = 0.5 / (2 ** (self.zoom_level - self.min_zoom))
        self.center_lon -= step
        self.load_current_tile()

    def pan_right(self):
        step = 0.5 / (2 ** (self.zoom_level - self.min_zoom))
        self.center_lon += step
        self.load_current_tile()

    def pan_up(self):
        step = 0.5 / (2 ** (self.zoom_level - self.min_zoom))
        self.center_lat += step
        self.load_current_tile()

    def pan_down(self):
        step = 0.5 / (2 ** (self.zoom_level - self.min_zoom))
        self.center_lat -= step
        self.load_current_tile()

    def exit(self):
        self.close()
