#!/bin/bash

version='1.3.1'
changelog='Introduce configurable translation engine allowing users to choose between gettext (local .po files) and Google Translate for UI translations. Features include:\n- New translation engine config option in plugin settings\n- Support for 100+ languages via Google Translate with automatic system language detection\n- Placeholder preservation logic to handle format strings in translated text\n- New "Translation Settings" menu item in main interface\n- Improved translation function with fallback mechanisms and error handling\n- Version bump to 1.3.0\n- Code formatting improvements (f-string to % formatting for Python 2 compatibility)\n- Enhanced documentation with section headers and docstrings'

TMPPATH=/tmp/ForecaOne-install
FILEPATH=/tmp/ForecaOne-main.tar.gz

# Config directory where user settings are stored
CONFIG_DIR="/etc/enigma2/foreca"
BACKUP_DIR="/tmp/foreca_backup"

if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/Foreca1
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/Foreca1
fi

echo "Starting ForecaOne installation..."


cleanup() {
    echo "Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
}

# Backup configuration if it exists
backup_config() {
    if [ -d "$CONFIG_DIR" ]; then
        echo "Backing up configuration from $CONFIG_DIR to $BACKUP_DIR ..."
        rm -rf "$BACKUP_DIR" 2>/dev/null
        cp -r "$CONFIG_DIR" "$BACKUP_DIR"
        if [ $? -eq 0 ]; then
            echo "Backup successful."
        else
            echo "Backup failed! Aborting."
            exit 1
        fi
    else
        echo "No existing configuration directory found. Skipping backup."
    fi
}

# Restore configuration after installation
restore_config() {
    if [ -d "$BACKUP_DIR" ]; then
        echo "Restoring configuration from $BACKUP_DIR to $CONFIG_DIR ..."
        mkdir -p "$CONFIG_DIR"
        cp -r "$BACKUP_DIR"/* "$CONFIG_DIR"/ 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "Configuration restored successfully."
        else
            echo "Warning: Failed to restore some configuration files."
        fi
        rm -rf "$BACKUP_DIR"
    fi
}

detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOs"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/var/lib/opkg/status"
    elif [ -f /etc/debian_version ]; then
        OSTYPE="Debian"
        STATUS="/var/lib/dpkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "Detected OS type: $OSTYPE"
}

detect_os

if ! command -v wget >/dev/null 2>&1; then
    echo "Installing wget..."
    case "$OSTYPE" in
        "DreamOs"|"Debian")
            apt-get update && apt-get install -y wget || { echo "Failed to install wget"; exit 1; }
            ;;
        "OE")
            opkg update && opkg install wget || { echo "Failed to install wget"; exit 1; }
            ;;
        *)
            echo "Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python3 image detected"
    PYTHON="PY3"
    Packagesix="python3-six"
    Packagerequests="python3-requests"
    Packagepillow="python3-pillow"
else
    echo "Python2 image detected"
    PYTHON="PY2"
    Packagerequests="python-requests"
    Packagepillow="python-pillow"
    if [ "$OSTYPE" = "DreamOs" ] || [ "$OSTYPE" = "Debian" ]; then
        Packagesix="python-six"
    else
        Packagesix="python-six"
    fi
fi

install_pkg() {
    local pkg=$1
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "Installing $pkg..."
        case "$OSTYPE" in
            "DreamOs"|"Debian")
                apt-get update && apt-get install -y "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            "OE")
                opkg update && opkg install "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            *)
                echo "Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "$pkg already installed"
    fi
}

[ "$PYTHON" = "PY3" ] && install_pkg "$Packagesix"
install_pkg "$Packagerequests"

if [ "$OSTYPE" = "OE" ]; then
    echo "Installing additional dependencies for OpenEmbedded..."
    for pkg in ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp; do
        install_pkg "$pkg"
    done
fi

cleanup
mkdir -p "$TMPPATH"

# Backup configuration before installing new version
backup_config

echo "Downloading ForecaOne..."
wget --no-check-certificate 'https://github.com/Belfagor2005/ForecaOne/archive/refs/heads/main.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download ForecaOne package!"
    cleanup
    exit 1
fi

echo "Extracting package..."
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "Failed to extract ForecaOne package!"
    cleanup
    exit 1
fi

echo "Installing plugin files..."
mkdir -p "$PLUGINPATH"

if [ -d "$TMPPATH/ForecaOne-main/usr/lib/enigma2/python/Plugins/Extensions/Foreca1" ]; then
    cp -r "$TMPPATH/ForecaOne-main/usr/lib/enigma2/python/Plugins/Extensions/Foreca1"/* "$PLUGINPATH/" 2>/dev/null
    echo "Copied from standard plugin directory"
elif [ -d "$TMPPATH/ForecaOne-main/usr/lib64/enigma2/python/Plugins/Extensions/Foreca1" ]; then
    cp -r "$TMPPATH/ForecaOne-main/usr/lib64/enigma2/python/Plugins/Extensions/Foreca1"/* "$PLUGINPATH/" 2>/dev/null
    echo "Copied from lib64 plugin directory"
elif [ -d "$TMPPATH/ForecaOne-main/usr" ]; then
    cp -r "$TMPPATH/ForecaOne-main/usr"/* /usr/ 2>/dev/null
    echo "Copied entire usr structure"
else
    echo "Could not find plugin files in extracted archive"
    echo "Available directories:"
    find "$TMPPATH" -type d -name "*ForecaOne*" | head -10
    cleanup
    exit 1
fi

sync

echo "Verifying installation..."
if [ -d "$PLUGINPATH" ] && [ -n "$(ls -A "$PLUGINPATH" 2>/dev/null)" ]; then
    echo "Plugin directory found and not empty: $PLUGINPATH"
    echo "Contents:"
    ls -la "$PLUGINPATH/" | head -10
else
    echo "Plugin installation failed or directory is empty!"
    cleanup
    exit 1
fi


# Restore user configuration after installing new version
restore_config
sync

FILE="/etc/image-version"
box_type=$(sed -n '1p' /etc/hostname 2>/dev/null || echo "Unknown")

# distro_value=$(grep '^distro=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
# distro_version=$(grep '^version=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
distro_value="Unknown"
distro_version="Unknown"
if [ -r /etc/os-release ]; then
    distro_value=$(grep '^NAME=' /etc/os-release 2>/dev/null | cut -d'"' -f2)
    distro_version=$(grep '^VERSION_ID=' /etc/os-release 2>/dev/null | cut -d'"' -f2)
elif [ -r /etc/issue ]; then
    distro_value=$(head -n 1 /etc/issue 2>/dev/null | awk '{print $1}')
    distro_version=$(head -n 1 /etc/issue 2>/dev/null | awk '{print $2}')
elif [ -r /etc/vtiversion.info ]; then
    distro_value=$(head -n 1 /etc/vtiversion.info 2>/dev/null)
elif [ -r /etc/issue.net ]; then
    distro_value=$(head -n 1 /etc/issue.net 2>/dev/null | awk '{print $1}')
    distro_version=$(head -n 1 /etc/issue.net 2>/dev/null | awk '{print $2}')
fi

[ -z "$distro_value" ] && distro_value="Unknown"
[ -z "$distro_version" ] && distro_version="Unknown"
python_vers=$(python --version 2>&1)


cat <<EOF

#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#           Please RESTART YOUR DEVICE FOR APPLY        #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
OS SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: ${distro_value:-Unknown}
IMAGE VERSION: ${distro_version:-Unknown}
PLUGIN VERSION: $version
EOF