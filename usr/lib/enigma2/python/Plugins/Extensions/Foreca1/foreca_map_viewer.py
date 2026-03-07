#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026
# foreca_map_viewer.py - Final: 16:9 output (1280x720), dynamic grid

from os import listdir, remove
from os.path import exists, join, basename
from math import log, tan, pi, radians, cos
from datetime import datetime

from PIL import Image, ImageStat

from enigma import getDesktop

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen

from Components.ActionMap import HelpableActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Label import Label

from .google_translate import trans
from . import (
    _,
    DEBUG,
    CACHE_BASE,
    THUMB_PATH,
    load_skin_for_class,
    apply_global_theme,
)

TILE_SIZE = 256
FINAL_WIDTH = 1280
FINAL_HEIGHT = 720


REGION_CENTERS = {
    'eu': (50.0, 10.0),
    'it': (42.5, 12.5),
    'de': (51.0, 10.0),
    'fr': (46.0, 2.0),
    'es': (40.0, -4.0),
    'uk': (54.0, -2.0),
    'pl': (52.0, 19.0),
    'nl': (52.0, 5.0),
    'be': (50.5, 4.5),
    'at': (47.5, 14.0),
    'ch': (46.8, 8.2),
    'us': (39.8, -98.5),
    'ca': (56.0, -106.0),
    'mx': (23.0, -102.0),
}


# -----------------------------------------------------------------------------
# Background selection based on coordinates
# -----------------------------------------------------------------------------

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


def create_composite_map(
    weather_tiles_path,
    layer_title,
    center_lat,
    center_lon,
    region=None,
    canvas_size=(
        FINAL_WIDTH,
        FINAL_HEIGHT)):
    BG_COLOR = (176, 196, 222)  # light steel blue
    canvas = Image.new("RGBA", canvas_size, BG_COLOR + (255,))

    # Geographic background (if available) – pass region hint
    # bg_file = get_background_for_layer(center_lat, center_lon, region)
    bg_file = get_background_for_layer(center_lat, center_lon)
    if bg_file:
        bg_path = join(THUMB_PATH, bg_file)
        if exists(bg_path):
            try:
                bg = Image.open(bg_path).convert("RGBA")
                bg = bg.resize(canvas_size, Image.Resampling.LANCZOS)
                canvas.paste(bg, (0, 0), bg)
            except Exception as e:
                print(f"[Composite] Background error: {e}")

    # Overlay the weather tiles
    if exists(weather_tiles_path):
        try:
            weather = Image.open(weather_tiles_path).convert("RGBA")
            weather = weather.resize(canvas_size, Image.Resampling.LANCZOS)
            # For layers with symbols (e.g., windsvg), we may want them more visible
            # Slightly increase opacity if needed
            # (optional, comment out if not required)
            # r, g, b, a = weather.split()
            # a = a.point(lambda x: min(255, int(x * 1.2)))
            # weather = Image.merge("RGBA", (r, g, b, a))
            canvas.paste(weather, (0, 0), weather)
        except Exception as e:
            print(f"[Composite] Weather tile error: {e}")
    else:
        print(f"[Composite] Tile not found: {weather_tiles_path}")

    composite_path = join(
        CACHE_BASE,
        f"composite_{basename(weather_tiles_path)}"
    )
    canvas.convert("RGB").save(composite_path, "PNG")
    return composite_path


class ForecaMapViewer(Screen, HelpableScreen):

    def __init__(self, session, api, layer, unit_system='metric', region='eu'):
        self.skin = load_skin_for_class(ForecaMapViewer)
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.api = api
        self.layer = layer
        self.layer_id = layer['id']
        self.layer_title = layer.get('title', 'Map')
        self.unit_system = unit_system
        self.region = region.lower()

        # Get layer extent if available
        extent = layer.get('extent', {})
        if extent and 'minLat' in extent and 'maxLat' in extent and 'minLon' in extent and 'maxLon' in extent:
            self.center_lat = (extent['minLat'] + extent['maxLat']) / 2.0
            self.center_lon = (extent['minLon'] + extent['maxLon']) / 2.0
            self.min_zoom = extent.get('minZoom', 2)
            self.max_zoom = extent.get('maxZoom', 21)

            # --- : if the extension is global, use the center of the region ---
            # We consider it global if it covers almost the entire planet
            if (extent['minLat'] <= -80 and extent['maxLat'] >= 80 and
                    extent['minLon'] <= -170 and extent['maxLon'] >= 170):
                if self.region in REGION_CENTERS:
                    old_lat, old_lon = self.center_lat, self.center_lon
                    self.center_lat, self.center_lon = REGION_CENTERS[self.region]
                    if DEBUG:
                        print(
                            f"[DEBUG] Layer globale ({old_lat},{old_lon}) → sovrascritto con centro regione '{self.region}': ({self.center_lat},{self.center_lon})")

            if DEBUG:
                print(
                    f"[DEBUG] Layer extent: lat {extent['minLat']}-{extent['maxLat']}, lon {extent['minLon']}-{extent['maxLon']}")
                print(
                    f"[DEBUG] Center: ({self.center_lat}, {self.center_lon})")
        else:
            # Fallback to region-based center
            if self.region in REGION_CENTERS:
                self.center_lat, self.center_lon = REGION_CENTERS[self.region]
            else:
                self.center_lat, self.center_lon = 50.0, 10.0
            self.min_zoom = 2
            self.max_zoom = 21
            if DEBUG:
                print(
                    f"[DEBUG] Using region center: ({self.center_lat}, {self.center_lon})")

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
            self.grid_cols = 9
            self.grid_rows = 7

        self.tile_size = TILE_SIZE
        self.map_w = self.grid_cols * self.tile_size
        self.map_h = self.grid_rows * self.tile_size

        # Compute initial zoom level based on latitude (if possible)
        try:
            lat_float = float(self.center_lat)
            # Heuristic: higher zoom near equator
            self.zoom_level = max(
                self.min_zoom, min(
                    self.max_zoom, int(
                        8 - abs(lat_float) / 15)))
        except (ValueError, TypeError):
            self.zoom_level = max(self.min_zoom, min(self.max_zoom, 5))

        # Get timestamps from layer
        self.timestamps = layer.get('times', {}).get('available', [])
        self.current_time_index = layer.get('times', {}).get('current', 0)
        self.setTitle(f"Foreca One: {self.layer_title}")

        self["map"] = Pixmap()
        self["title"] = Label(self.layer_title)
        self["layerinfo"] = Label("")
        self["time"] = Label(_("Loading..."))
        self["info"] = Label(_("Use ← → to change time | OK to exit"))
        self['key_red'] = StaticText(_("Exit"))
        self['key_green'] = StaticText(_("Zoom+"))
        self['key_yellow'] = StaticText(_("Zoom-"))
        self['key_blue'] = StaticText()
        self['zoom_label'] = Label(_("Zoom: ") + str(self.zoom_level))
        self["background_plate"] = Label("")
        self["selection_overlay"] = Label("")
        self["actions"] = HelpableActionMap(
            self, "ForecaActions",
            {
                "cancel": (self.exit, _("Exit")),
                "red": (self.exit, _("Exit")),
                "left": (self.prev_time, _("Prev")),
                "right": (self.next_time, _("Next")),
                "green": (self.zoom_in, _("Zoom+")),
                "yellow": (self.zoom_out, _("Zoom-")),
                "nextBouquet": (self.zoom_in, _("Zoom+")),
                "prevBouquet": (self.zoom_out, _("Zoom-"))
            },
            -1
        )
        self.clear_cache()
        self.widget_width = 1819
        self.widget_height = 853
        self.onLayoutFinish.append(self.get_widget_size)
        self.onLayoutFinish.append(self.load_current_tile)
        self.onLayoutFinish.append(self._apply_theme)

    def get_widget_size(self):
        if "map" in self and self["map"].instance:
            size = self["map"].instance.size()
            self.widget_width = size.width()
            self.widget_height = size.height()
            if DEBUG:
                print(
                    f"[DEBUG] Widget map size: {self.widget_width}x{self.widget_height}")

    def _apply_theme(self):
        apply_global_theme(self)

    def clear_cache(self):
        try:
            if exists(CACHE_BASE):
                for f in listdir(CACHE_BASE):
                    if f.endswith('.png'):
                        remove(join(CACHE_BASE, f))
                if DEBUG:
                    print("[Foreca1] Cache cleaned")
        except Exception as e:
            print(f"[Foreca1] Error clean cache: {e}")

    def latlon_to_tile(self, lat, lon, zoom):
        lat_rad = radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - log(tan(lat_rad) + 1.0 / cos(lat_rad)) / pi) / 2.0 * n)
        return x, y

    def load_current_tile(self):
        if not self.timestamps:
            from datetime import datetime
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            self.timestamps = [now]
            self.current_time_index = 0
            self["time"].setText(_("Using current time"))

        if self.current_time_index >= len(self.timestamps):
            self.current_time_index = 0

        timestamp = self.timestamps[self.current_time_index]

        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            display_time = dt.strftime("%d/%m %H:%M UTC")
        except BaseException:
            display_time = timestamp

        self["time"].setText(f"{display_time}")
        self["zoom_label"].setText(f"Zoom: {self.zoom_level}")
        self["info"].setText(_("Downloading tiles..."))
        self.download_tile_grid_async(timestamp, self.tile_grid_downloaded)

    def download_tile_grid_async(self, timestamp, callback):
        def download_thread():
            cx, cy = self.latlon_to_tile(
                self.center_lat, self.center_lon, self.zoom_level)
            offset_cols = self.grid_cols // 2
            offset_rows = self.grid_rows // 2

            tile_paths = []
            for dx in range(-offset_cols, offset_cols + 1):
                for dy in range(-offset_rows, offset_rows + 1):
                    tx = cx + dx
                    ty = cy + dy
                    path = self.api.get_tile(
                        self.layer_id,
                        timestamp,
                        self.zoom_level,
                        tx, ty,
                        self.unit_system
                    )

                    if path and exists(path):
                        try:
                            if DEBUG:
                                with Image.open(path) as img:
                                    print(
                                        f"[DEBUG] Tile zoom={self.zoom_level} ({tx},{ty}) size: {img.size}")
                            tile_paths.append(
                                (dx + offset_cols, dy + offset_rows, path))
                        except Exception as e:
                            print(
                                f"[Foreca1] Tile corrotta, saltata: {path} - {e}")
                            try:
                                remove(path)
                            except BaseException:
                                pass
            if DEBUG:
                print(f"[DEBUG] Tile valide scaricate: {len(tile_paths)}")
            if len(tile_paths) > 0:
                merged = self.merge_tile_grid(tile_paths)
                if merged and callback:
                    callback(merged)
            else:
                if DEBUG:
                    print("[Foreca1] No downloaded tiles")
                from twisted.internet import reactor
                reactor.callFromThread(self._show_no_tiles_error)
                callback(None)

        from threading import Thread
        Thread(target=download_thread).start()

    def is_uniform_tile(self, pil_image, threshold=10):
        """
        Returns True if the image is likely a placeholder (uniform color).
        threshold: maximum standard deviation to consider the image uniform.
        """
        try:
            # Analyze standard deviation
            stat = ImageStat.Stat(pil_image.convert("RGB"))
            std_r, std_g, std_b = stat.stddev
            if std_r < threshold and std_g < threshold and std_b < threshold:
                # Mean color
                mean_r, mean_g, mean_b = stat.mean
                # Typical placeholders: pink (R>200, G<200, B>200) or uniform
                # grays (R,G,B close)
                if (mean_r > 200 and mean_g < 200 and mean_b > 200) or \
                   (abs(mean_r - mean_g) < 20 and abs(mean_g - mean_b) < 20):
                    return True
            return False
        except Exception as e:
            print(f"[Foreca1] Error in is_uniform_tile: {e}")
            return False

    def _show_no_tiles_error(self):
        self["time"].setText(_("No tiles available"))
        self["info"].setText(_("Try different zoom or region"))

    def merge_tile_grid(self, tile_paths):
        try:
            merged = Image.new('RGBA', (self.map_w, self.map_h), (0, 0, 0, 0))

            for col, row, path in tile_paths:
                try:
                    tile = Image.open(path).convert('RGBA')
                except Exception as e:
                    print(f"[Foreca1] Tile corrotta, saltata: {path} - {e}")
                    continue

                # Debug suspicious tile (adjust coordinates if necessary)
                if DEBUG:
                    if col == 10 and row == 7:
                        colors = tile.convert('RGB').getcolors(maxcolors=256)
                        print(f"[DEBUG] Tile (10,7) colors: {colors}")
                        stat = ImageStat.Stat(tile.convert('RGB'))
                        print(
                            f"[DEBUG] Tile (10,7) mean: {stat.mean}, stddev: {stat.stddev}")
                """
                if self.is_uniform_tile(tile):
                    if DEBUG:
                        print(
                            f"[Foreca1] Tile uniforme saltata: ({col},{row}) {path}")
                    continue
                """
                x = col * self.tile_size
                y = row * self.tile_size
                merged.paste(tile, (x, y), tile)

            merged_path = join(CACHE_BASE,
                               f"merged_{self.layer_id}_{self.zoom_level}.png")
            merged.save(merged_path, 'PNG')
            return merged_path

        except Exception as e:
            print(f"[Foreca1] Errore merge: {e}")
            import traceback
            traceback.print_exc()
            return None

    def tile_grid_downloaded(self, merged_image_path):
        if merged_image_path and exists(merged_image_path):
            try:
                composite_path = create_composite_map(
                    merged_image_path,
                    self.layer_title,
                    self.center_lat,
                    self.center_lon,
                    region=self.region,
                    canvas_size=(self.map_w, self.map_h)
                )

                # Resize to widget size to avoid distortion
                if composite_path and exists(composite_path):
                    img = Image.open(composite_path)
                    if hasattr(self, 'widget_width') and self.widget_width > 0:
                        img = img.resize(
                            (self.widget_width, self.widget_height), Image.Resampling.LANCZOS)
                        resized_path = composite_path.replace(
                            '.png', '_widget.png')
                        img.save(resized_path, 'PNG')
                        self["map"].instance.setPixmapFromFile(resized_path)
                    else:
                        self["map"].instance.setPixmapFromFile(composite_path)
                    self["map"].instance.show()

                self.update_layer_info()

                current_time = self.timestamps[self.current_time_index]
                try:
                    dt = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")
                    display_time = dt.strftime("%d/%m %H:%M UTC")
                except BaseException:
                    display_time = current_time

                self["time"].setText(
                    f"{display_time} | Zoom: {self.zoom_level} | Grid: {self.grid_cols}x{self.grid_rows}")
                self["info"].setText(_("Image Downloaded"))

            except Exception as e:
                print(f"[Foreca1] Display error: {e}")
                import traceback
                traceback.print_exc()
                self["time"].setText(_("Error displaying map"))
        else:
            self["time"].setText(_("No tiles available"))
            self["info"].setText(_("Try different zoom or layer"))

    def update_layer_info(self):
        try:
            layer_name = self.layer_title
            data_type = self.get_data_type_from_layer(layer_name)
            region_name = self.region.upper()
            unit = "Metric" if self.unit_system == 'metric' else "Imperial"
            self["layerinfo"].setText(f"{data_type} - {region_name} ({unit})")
        except BaseException:
            self["layerinfo"].setText(self.layer_title)

    def get_layer_type(self):
        """Restituisce il tipo di layer (png, windsvg, ecc.)"""
        return self.layer.get('type', 'png')

    def get_data_type_from_layer(self, layer_name):
        layer_lower = layer_name.lower()
        if 'temp' in layer_lower:
            return trans("Temperature")
        elif 'wind' in layer_lower:
            return trans("Wind")
        elif 'cloud' in layer_lower:
            return trans("Cloud Cover")
        elif 'precip' in layer_lower or 'rain' in layer_lower:
            return trans("Precipitation")
        elif 'pressure' in layer_lower:
            return trans("Pressure")
        elif 'snow' in layer_lower:
            return trans("Snow")
        elif 'radar' in layer_lower:
            return trans("Radar")
        else:
            return trans(layer_name)

    def zoom_in(self):
        if self.zoom_level < self.max_zoom:
            self.zoom_level += 1
            self._adjust_grid_to_widget()
            self.load_current_tile()

    def zoom_out(self):
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= 1
            self._adjust_grid_to_widget()
            self.load_current_tile()

    def _adjust_grid_to_widget(self):
        if "map" in self and self["map"].instance:
            w = self["map"].instance.size().width()
            h = self["map"].instance.size().height()
            self.grid_cols = (w + self.tile_size - 1) // self.tile_size
            self.grid_rows = (h + self.tile_size - 1) // self.tile_size
            self.map_w = self.grid_cols * self.tile_size
            self.map_h = self.grid_rows * self.tile_size

    def prev_time(self):
        if len(self.timestamps) > 1:
            self.current_time_index = (
                self.current_time_index - 1) % len(self.timestamps)
            self.load_current_tile()

    def next_time(self):
        if len(self.timestamps) > 1:
            self.current_time_index = (
                self.current_time_index + 1) % len(self.timestamps)
            self.load_current_tile()

    def exit(self):
        self.close()
