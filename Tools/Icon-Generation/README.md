## Description

This is a tool for generating RocketMap's base Pokémon icons.

## Install

To use this tool you need:
* Pillow - a python image library (a replacement for PIL)
* The Arial Bold truetype font

To install pillow run `pip install pillow`.

Installation of the Arial Bold font varies by platform. In Windows, it will typically be available by default. For linux systems, you may need to install the package `ttf-mscorefonts-installer` (or the equivallent package for your platform).

## Usage

To generate the standard 94x94 icons and save them to the `static/icons/` directory, run:

`generate_icons.py`

To set a different output location, set the `-o` parameter:

`generate_icons.py -o OUTPUT_DIR`

To generate icons of a different size, set the `-s` parameter:

`generate_icons.py -s SIZE`
