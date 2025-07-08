#!/bin/bash
# Compile all .py files in lib/ to .mpy for MicroPython deployment (Raspberry Pi Pico)
# Usage: ./compile_mpy.sh

set -e

# Path to mpy-cross (adjust if needed)
MPY_CROSS=mpy-cross

# Check if mpy-cross is available
if ! command -v "$MPY_CROSS" &> /dev/null; then
    echo "Error: mpy-cross not found in PATH."
    echo "Build it from https://github.com/micropython/micropython/tree/master/mpy-cross"
    exit 1
fi

# Source and destination directories
SRC_DIR="lib"
DST_DIR="dist/lib"

# Create dist directory
rm -rf dist
mkdir -p "$DST_DIR"

# Copy __init__.py if present
if [ -f "$SRC_DIR/__init__.py" ]; then
    cp "$SRC_DIR/__init__.py" "$DST_DIR/"
fi

# Compile all .py files to .mpy
for f in "$SRC_DIR"/*.py; do
    if [ -f "$f" ]; then
        echo "Compiling $f..."
        "$MPY_CROSS" "$f"
        mv "${f%.py}.mpy" "$DST_DIR/"
    fi
done

echo "Compilation complete."
echo "Deploy all files from dist/ to your Pico (lib/ directory)."
