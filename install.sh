#!/bin/sh
# Rt:Terminal I.D. v4.0 - Installer
# SPDW Factory - RSPDW Chou Henka Project

echo "========================================"
echo "  Rt:Terminal I.D. v4.0 Installer"
echo "  SPDW Factory"
echo "========================================"

TARGET_DIR="/home/retrofw/.rspdw/rt_terminal"
FONT_DIR="$TARGET_DIR/fonts"

echo "Creating directories..."
mkdir -p "$TARGET_DIR"
mkdir -p "$FONT_DIR"

echo "Installing files..."
cp main.py "$TARGET_DIR/"
cp rt_tid.json "$TARGET_DIR/"
cp icon.png "$TARGET_DIR/"
cp manual.txt "$TARGET_DIR/"

if [ -f "default.gcw0.desktop" ]; then
    echo "Installing desktop launcher..."
    cp default.gcw0.desktop "$TARGET_DIR/"
fi

echo "Setting permissions..."
chmod +x "$TARGET_DIR/main.py"

echo ""
echo "Installation complete!"
echo "Files installed to: $TARGET_DIR"
echo ""
echo "To run: python2 $TARGET_DIR/main.py"
echo "========================================"
