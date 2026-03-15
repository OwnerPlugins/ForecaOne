#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) @Lululla 2026

from __future__ import absolute_import

from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.Language import language
from os.path import exists, join, dirname
from enigma import getDesktop, gRGB
from skin import parseColor
from os import makedirs, listdir, environ
import gettext
import codecs

VERSION = "1.1.3"
_AUTHOR_ = "by Lululla - 2026"
IDEAS = "@Bauernbub"
THANKS = "@Orlandox"
BASEURL = "https://www.foreca.com/"
TEMP_DIR = '/tmp/foreca'
SYSTEM_DIR = '/etc/enigma2/foreca'
PLUGIN_PATH = dirname(__file__)
SKINS_PATH = join(PLUGIN_PATH, "skins")
MOON_ICON_PATH = join(PLUGIN_PATH, "moon")
CONFIG_FILE = join(SYSTEM_DIR, "api_config.txt")
DATA_FILE = join(SYSTEM_DIR, "color_database.txt")
CACHE_BASE = join(TEMP_DIR, "foreca_map_cache")
THUMB_PATH = join(PLUGIN_PATH, "thumb/")
DBG_DIR = join(PLUGIN_PATH, 'debug')
TOKEN_FILE = join(CACHE_BASE, "token.json")
WETTERKONTOR_CACHE = join(CACHE_BASE, "wetterkontor/")
INSTALLER_URL = "https://raw.githubusercontent.com/Belfagor2005/ForecaOne/main/installer.sh"

DEBUG = True
CACHE_EXPIRE = 3600

if not exists(SYSTEM_DIR):
    makedirs(SYSTEM_DIR)

if not exists(TEMP_DIR):
    makedirs(TEMP_DIR)

if not exists(DBG_DIR):
    makedirs(DBG_DIR)

if not exists(CACHE_BASE):
    makedirs(CACHE_BASE)

if not exists(WETTERKONTOR_CACHE):
    makedirs(WETTERKONTOR_CACHE)

PluginLanguageDomain = "Foreca"
PluginLanguagePath = "Extensions/Foreca1/locale"
isDreambox = exists("/usr/bin/apt-get")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}


def localeInit():
    if isDreambox:
        lang = language.getLanguage()[:2]
        environ["LANGUAGE"] = lang
    if PluginLanguageDomain and PluginLanguagePath:
        gettext.bindtextdomain(
            PluginLanguageDomain,
            resolveFilename(
                SCOPE_PLUGINS,
                PluginLanguagePath))


if isDreambox:
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translated = gettext.dgettext(PluginLanguageDomain, txt)
        if translated:
            return translated
        else:
            print(
                "[%s] fallback to default translation for %s" %
                (PluginLanguageDomain, txt))
            return gettext.gettext(txt)


localeInit()
language.addCallback(localeInit)


# ============ DETECT SCREEN RESOLUTION ============
def get_screen_resolution():
    """Get current screen resolution"""
    desktop = getDesktop(0)
    return desktop.size()


def get_resolution_type():
    """Get resolution type: hd, fhd, wqhd"""
    width = get_screen_resolution().width()

    if width >= 2560:
        return 'wqhd'
    elif width >= 1920:
        return 'fhd'
    else:  # 1280x720 or smaller
        return 'hd'


def load_skin_by_class(class_name):
    """Load skin using class name and current resolution"""
    if DEBUG:
        print("\n" + "=" * 60)
        print(f"[SKIN DEBUG] Looking for skin: '{class_name}'")
        print(f"[SKIN DEBUG] SKINS_PATH = {SKINS_PATH}")
        # List all skins folders
        if exists(SKINS_PATH):
            print(f"[SKIN DEBUG] Contents of {SKINS_PATH}:")
            for item in listdir(SKINS_PATH):
                print(f"  - {item}")
        else:
            print("[SKIN DEBUG] SKINS_PATH does NOT exist!")

    resolution = get_resolution_type()
    if DEBUG:
        print(f"[SKIN DEBUG] resolution = {resolution}")

    skin_file = join(SKINS_PATH, resolution, f"{class_name}.xml")
    if DEBUG:
        print(f"[SKIN DEBUG] Trying: {skin_file}")
        print(f"[SKIN DEBUG] Exists? {exists(skin_file)}")

    if not exists(skin_file):
        print("[SKIN DEBUG] NOT FOUND, trying HD fallback")
        skin_file = join(SKINS_PATH, "hd", f"{class_name}.xml")
        print(f"[SKIN DEBUG] Trying: {skin_file}")
        print(f"[SKIN DEBUG] Exists? {exists(skin_file)}")

    if exists(skin_file):
        if DEBUG:
            print("[SKIN DEBUG] ✓ FOUND! Loading file...")
        try:
            with codecs.open(skin_file, 'r', 'utf-8') as f:
                content = f.read()
                if DEBUG:
                    print(f"[SKIN DEBUG] ✓ Loaded {len(content)} bytes")
                    print(
                        f"[SKIN DEBUG] First 100 chars: {content[:100].replace(chr(10), ' ')}")
                    print("=" * 60 + "\n")
                return content
        except Exception as e:
            print(f"[SKIN DEBUG] ✗ Error reading file: {e}")
    else:
        print(f"[SKIN DEBUG] ✗ SKIN FILE MISSING: {skin_file}")
    if DEBUG:
        print("=" * 60 + "\n")
    return None


def load_skin_for_class(cls):
    return load_skin_by_class(cls.__name__)


def apply_global_theme(screen):
    """
    Applies the background color (from set_color.conf) and transparency (from set_alpha.conf)
    to the standard 'background_plate' and 'selection_overlay' widgets on the screen.
    """
    color_file = join(SYSTEM_DIR, "set_color.conf")
    alpha_file = join(SYSTEM_DIR, "set_alpha.conf")

    # Background color
    if exists(color_file):
        try:
            with open(color_file, "r") as f:
                parts = f.read().strip().split()
                if len(parts) >= 3:
                    r, g, b = parts[0], parts[1], parts[2]
                    bg_color = gRGB(int(r), int(g), int(b))
                    if "background_plate" in screen:
                        screen["background_plate"].instance.setBackgroundColor(
                            bg_color)
        except Exception as e:
            print("[Theme] Error loading color:", e)

    # transparency
    if exists(alpha_file):
        try:
            with open(alpha_file, "r") as f:
                alpha = f.read().strip()
                if "selection_overlay" in screen:
                    screen["selection_overlay"].instance.setBackgroundColor(
                        parseColor(alpha))
        except Exception as e:
            print("[Theme] Error loading alpha:", e)


def get_icon_path(icon_name, fallback='na.png'):
    """
    Returns the full path of an icon from the thumb/ folder.
    If the file does not exist, returns the path of the fallback icon (na.png).
    """
    path = join(THUMB_PATH, icon_name)
    if exists(path):
        return path

    # Fallback to the na.png icon
    fallback_path = join(THUMB_PATH, fallback)
    return fallback_path if exists(fallback_path) else None


def cleanup_temp_files():
    """Removes the temporary folder and all SVG files inside it."""
    import shutil
    if exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            if DEBUG:
                print(f"[Meteogram] Cleaned folder {TEMP_DIR}")
        except Exception as e:
            print(f"[Meteogram] Error cleaning {TEMP_DIR}: {e}")

    if exists(DBG_DIR):
        try:
            shutil.rmtree(DBG_DIR)
            if DEBUG:
                print(f"[Meteogram] Cleaned folder {DBG_DIR}")
        except Exception as e:
            print(f"[Meteogram] Error cleaning {DBG_DIR}: {e}")


"""
def apply_global_theme(screen):
    '''
    Apply background color (from set_color.conf) and transparency (from set_alpha.conf)
    to all widgets of the screen that have meaningful names:
    - Widgets with names starting with 'color_bg_' or 'background_plate' or 'selection_overlay' receive the color.
    - Widgets with names starting with 'transp_bg_' receive the transparency.
    '''
    color_file = join(PLUGIN_PATH, "set_color.conf")
    alpha_file = join(PLUGIN_PATH, "set_alpha.conf")

    # Default color
    r, g, b = 0, 80, 239
    if exists(color_file):
        try:
            with open(color_file, "r") as f:
                parts = f.read().strip().split()
                if len(parts) >= 3:
                    r, g, b = parts[0], parts[1], parts[2]
        except Exception as e:
            print("[Theme] Error loading color:", e)
    bg_color = gRGB(int(r), int(g), int(b))

    # Default transparency
    alpha = '#40000000'
    if exists(alpha_file):
        try:
            with open(alpha_file, "r") as f:
                alpha = f.read().strip()
        except Exception as e:
            print("[Theme] Error loading alpha:", e)
    transparent_color = parseColor(alpha)

    # Apply to all widgets
    for name, widget in screen.items():
        if not hasattr(widget, 'instance') or not widget.instance:
            continue
        if name.startswith("color_bg_") or name in ["background_plate", "selection_overlay"]:
            widget.instance.setBackgroundColor(bg_color)
            widget.instance.invalidate()
        elif name.startswith("transp_bg_"):
            widget.instance.setBackgroundColor(transparent_color)
            widget.instance.invalidate()
"""
