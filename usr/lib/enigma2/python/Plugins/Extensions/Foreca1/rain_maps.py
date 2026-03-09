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
from . import (
    _,
    # DEBUG,
    load_skin_for_class,
    apply_global_theme,
    TEMP_DIR,
    THUMB_PATH,
    HEADERS
)
RAIN_MAPS_DIR = join(TEMP_DIR, "rainviewer")
if not exists(RAIN_MAPS_DIR):
    makedirs(RAIN_MAPS_DIR)

TILE_SIZE = 256
API_URL = "https://api.rainviewer.com/public/weather-maps.json"


# ---------------------------------------------
# Funzione per selezionare lo sfondo geografico
# ---------------------------------------------
def get_background_for_layer(lat, lon, region=None):
    """
    Return the filename of a geographic background image.
    The region parameter (e.g., 'eu', 'us') has highest priority.
    If region is not provided or the corresponding file is missing,
    fall back to coordinate-based selection using precise continental extents.
    """
    # 1) Priority: Known region (specific layer)
    if region:
        region_map = {
            'eu': 'europa.png',
            'europe': 'europa.png',
            'us': 'nordamerika.png',
            'usa': 'nordamerika.png',
            'it': 'italien.png',
            'italy': 'italien.png',
            'de': 'deutschland.png',
            'germany': 'deutschland.png',
            'fr': 'frankreich.png',
            'france': 'frankreich.png',
            'uk': 'grossbritannien.png',
            'gb': 'grossbritannien.png',
            'es': 'spanien.png',
            'spain': 'spanien.png',
            'at': 'oesterreich.png',
            'austria': 'oesterreich.png',
            'ch': 'schweiz.png',
            'switzerland': 'schweiz.png',
        }
        reg_low = region.lower()
        if reg_low in region_map:
            fname = region_map[reg_low]
            if exists(join(THUMB_PATH, fname)):
                print(
                    f"[DEBUG] get_background: using region {region} -> {fname}")
                return fname
            else:
                print(
                    f"[DEBUG] get_background: region {region} file {fname} not found")

    # 2) Selection based on the precise coordinates of the continents
    # Europa (lat 36°N - 71°N, lon 9°34'W - 66°10'E)
    if -9.57 <= lon <= 66.17 and 36 <= lat <= 71.13:
        if exists(join(THUMB_PATH, 'europa.png')):
            print("[DEBUG] get_background: coordinate-based -> europa.png")
            return 'europa.png'

    # Africa (lat 34°51'S - 37°21'N, lon 17°33'W - 51°28'E)
    if -17.56 <= lon <= 51.46 and -34.85 <= lat <= 37.35:
        if exists(join(THUMB_PATH, 'africa.png')):
            print("[DEBUG] get_background: coordinate-based -> africa.png")
            return 'africa.png'

    # Asia (lat 1°16'S - 77°43'N, lon 26°04'E - 169°40'W)
    if (26.07 <= lon <= 180) and -1.27 <= lat <= 77.72:
        if exists(join(THUMB_PATH, 'asia.png')):
            print("[DEBUG] get_background: coordinate-based -> asia.png")
            return 'asia.png'
    if (-180 <= lon <= -169.67) and -1.27 <= lat <= 77.72:
        if exists(join(THUMB_PATH, 'asia.png')):
            print("[DEBUG] get_background: coordinate-based -> asia.png")
            return 'asia.png'

    # Nord America (lat 7°12'N - 83°40'N, lon 172°27'E - 12°08'W)
    if (lon >= -180 and lon <= -12.13) and 7.2 <= lat <= 83.67:
        if exists(join(THUMB_PATH, 'nordamerika.png')):
            print("[DEBUG] get_background: coordinate-based -> nordamerika.png")
            return 'nordamerika.png'
    if (lon >= 172.45 and lon <= 180) and 7.2 <= lat <= 83.67:
        if exists(join(THUMB_PATH, 'nordamerika.png')):
            print("[DEBUG] get_background: coordinate-based -> nordamerika.png")
            return 'nordamerika.png'

    # Sud America (lat 12°27'N - 56°30'S, lon 81°20'W - 34°47'W)
    if -81.33 <= lon <= -34.78 and -56.5 <= lat <= 12.45:
        if exists(join(THUMB_PATH, 'suedamerika.png')):
            print("[DEBUG] get_background: coordinate-based -> suedamerika.png")
            return 'suedamerika.png'

    # Oceania (lat 55°03'S - 28°38'N, lon 110°E - 180°)
    if 110 <= lon <= 180 and -55.05 <= lat <= 28.63:
        if exists(join(THUMB_PATH, 'oceania.png')):
            print("[DEBUG] get_background: coordinate-based -> oceania.png")
            return 'oceania.png'

    # Antartide (lat < -60°)
    if lat <= -60:
        if exists(join(THUMB_PATH, 'antarctica.png')):
            print("[DEBUG] get_background: coordinate-based -> antarctica.png")
            return 'antarctica.png'

    # 3) Fallback globale
    if exists(join(THUMB_PATH, 'world.png')):
        print("[DEBUG] get_background: fallback -> world.png")
        return 'world.png'

    print("[DEBUG] get_background: no background found")
    return None


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

        # Coordinate di default (centro Europa)
        self.center_lat = 50.0
        self.center_lon = 10.0
        # self.center_lat = 35.71
        # self.center_lon = -70.87

        self.zoom = 5
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

        # Widget
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
        self['zoom_label'] = Label(_("Zoom: ") + str(self.zoom))

        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")

        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.exit, _("Exit")),
                "red": (self.exit, _("Exit")),
                "green": (self.zoom_in, _("Zoom+")),
                "yellow": (self.zoom_out, _("Zoom-")),
                "left": (self.prev_frame, _("Previous frame")),
                "right": (self.next_frame, _("Next frame")),
            },
            -1
        )

        self.onLayoutFinish.append(self._apply_theme)
        self.onLayoutFinish.append(self.load_frame_list)

    def _apply_theme(self):
        apply_global_theme(self)

    def load_frame_list(self):
        """Scarica il JSON e ottiene l'elenco dei frame disponibili"""
        self["info"].setText(_("Fetching radar data..."))
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
            self.frames.reverse()  # dal più vecchio al più recente
            self.current_frame = len(self.frames) - 1  # ultimo frame
            print(
                f"[RainViewer] {len(self.frames)} frames disponibili, host: {self.host}")
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
        timestamp = frame_path.split('/')[-1]  # estrae il numero
        try:
            dt = datetime.utcfromtimestamp(int(timestamp))
            time_str = dt.strftime("%d/%m %H:%M UTC")
        except BaseException:
            time_str = timestamp
        self["time_label"].setText(_("Frame: {}").format(time_str))
        self["info"].setText(_("Loading tiles..."))
        print(f"[RainViewer] Caricamento frame: {frame_path}")
        self.download_tiles(frame_path)

    def download_tiles(self, frame_path):
        """Scarica e compone le tile per il frame selezionato"""
        Thread(target=self._download_thread, args=(frame_path,)).start()

    def _download_thread(self, frame_path):
        cx, cy = self.latlon_to_tile(
            self.center_lat, self.center_lon, self.zoom)
        offset_cols = self.grid_cols // 2
        offset_rows = self.grid_rows // 2

        tile_paths = []
        for dx in range(-offset_cols, offset_cols + 1):
            for dy in range(-offset_rows, offset_rows + 1):
                x = cx + dx
                y = cy + dy
                url = self.build_tile_url(frame_path, x, y, self.zoom)
                path = self.download_tile(url)
                if path:
                    tile_paths.append(
                        (dx + offset_cols, dy + offset_rows, path))
                else:
                    print(f"[RainViewer] Tile non scaricata: {url}")

        print(f"[RainViewer] Scaricate {len(tile_paths)} tile")
        if tile_paths:
            merged = self.merge_tiles(tile_paths)
            if merged:
                print(f"[RainViewer] Immagine composita creata: {merged}")
                reactor.callFromThread(self.show_map, merged)
            else:
                reactor.callFromThread(
                    lambda: self["info"].setText(
                        _("Merge failed")))
        else:
            reactor.callFromThread(
                lambda: self["info"].setText(
                    _("No tiles downloaded")))

    def build_tile_url(self, frame_path, x, y, z):
        # Parametri fissi: size=256, colore=2 (verde-rosso), opzioni=1_1 (blur
        # + neve)
        return f"{self.host}{frame_path}/256/{z}/{x}/{y}/2/1_1.png"

    def download_tile(self, url):
        import hashlib
        cache_file = join(
            RAIN_MAPS_DIR, hashlib.md5(
                url.encode()).hexdigest() + '.png')
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

    # def merge_tiles(self, tile_paths):
        # try:
        # merged = Image.new('RGBA', (self.map_w, self.map_h), (0, 0, 0, 255))
        # for col, row, path in tile_paths:
        # tile = Image.open(path).convert('RGBA')
        # x = col * TILE_SIZE
        # y = row * TILE_SIZE
        # merged.paste(tile, (x, y), tile)
        # merged_rgb = merged.convert('RGB')
        # out_path = join(RAIN_MAPS_DIR, 'merged.jpg')
        # merged_rgb.save(out_path, 'JPEG', quality=90)
        # return out_path
        # except Exception as e:
        # print(f"[RainViewer] merge error: {e}")
        # return None

    def merge_tiles(self, tile_paths):
        try:
            bg_file = get_background_for_layer(
                self.center_lat, self.center_lon)
            if bg_file:
                bg_path = join(THUMB_PATH, bg_file)
                bg = Image.open(bg_path).convert("RGBA")
                bg = bg.resize((self.map_w, self.map_h),
                               Image.Resampling.LANCZOS)
                merged = bg.copy()
            else:
                merged = Image.new(
                    'RGBA', (self.map_w, self.map_h), (64, 64, 64, 255))

            for col, row, path in tile_paths:
                tile = Image.open(path).convert('RGBA')
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                merged.paste(tile, (x, y), tile)

            out_path = join(RAIN_MAPS_DIR, 'merged.png')
            merged.save(out_path)
            return out_path
        except Exception as e:
            print(f"[RainViewer] merge error: {e}")
            return None

    def show_map(self, path):
        from PIL import Image
        img = Image.open(path)
        # Ottieni le dimensioni del widget map
        widget_width = self["map"].instance.size().width()
        widget_height = self["map"].instance.size().height()
        # Ridimensiona mantenendo le proporzioni? Forse meglio riempire
        img_resized = img.resize(
            (widget_width, widget_height), Image.Resampling.LANCZOS)
        resized_path = path.replace('.png', '_widget.png')
        img_resized.save(resized_path)
        self["map"].instance.setPixmapFromFile(resized_path)
        self["map"].instance.show()
        self["info"].setText(_("Map loaded"))

    def latlon_to_tile(self, lat, lon, zoom):
        lat_rad = radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - log(tan(lat_rad) + 1.0 / cos(lat_rad)) / pi) / 2.0 * n)
        return x, y

    def zoom_in(self):
        if self.zoom < self.max_zoom:
            self.zoom += 1
            self['zoom_label'].setText(_("Zoom: ") + str(self.zoom))
            self.update_frame_display()

    def zoom_out(self):
        if self.zoom > self.min_zoom:
            self.zoom -= 1
            self['zoom_label'].setText(_("Zoom: ") + str(self.zoom))
            self.update_frame_display()

    def prev_frame(self):
        if self.current_frame > 0:
            self.current_frame -= 1
            self.update_frame_display()

    def next_frame(self):
        if self.current_frame < len(self.frames) - 1:
            self.current_frame += 1
            self.update_frame_display()

    def exit(self):
        self.close()
