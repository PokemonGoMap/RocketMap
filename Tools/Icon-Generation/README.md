## Description

This is a tool for generating RocketMap's base Pokémon icons.

## Install

To use this tool you need:
* Pillow - a python image library (a replacement for PIL)
* The Arial Bold truetype font

To install pillow run `pip install --upgrade -r requirements.txt`.

Installation of the Arial Bold font varies by platform:

### Windows

Arial Bold is typically available by default.

### Mac

Arial Bold is typically available by default.

### Linux

You may need to install the package `ttf-mscorefonts-installer` (or the equivalent package for your platform) and accept the Microsoft EULA.

e.g. `sudo apt-get install ttf-mscorefonts-installer`

## Usage

To generate the standard 94x94 icons and save them to the `static/icons/` directory, run:

python `generate_icons.py`

To set a different output location, set the `-o` parameter:

python `generate_icons.py -o OUTPUT_DIR`

To generate icons of a different size, set the `-s` parameter:

python `generate_icons.py -s SIZE`
