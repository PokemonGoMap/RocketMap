## Description

This is a tool to generate RocketMap's base Pokémon icons.

## Install

To use this tool you need:
* Pillow - a python image library (a replacement for PIL)
* The Arial Bold truetype font

### Pillow

Depending on your platform, you may need to install some dependencies first. Scripts which install the required dependencies (for some platforms) can be found at https://github.com/python-pillow/Pillow/tree/master/depends.

Note: some platforms automatically install the required dependencies for you through pip. If you can't find an install script for your platform, it may be because it is not necessary for you to install the dependencies manually.

Once you have the necessary dependencies installed, install pillow by running the command:
`pip install --upgrade -r requirements.txt`.

### Arial Bold

#### Windows

Arial Bold is typically available by default.

#### OSX

Arial Bold is typically available by default.

#### Linux

You may need to install the package `ttf-mscorefonts-installer` (or the equivalent package for your platform) and accept the Microsoft EULA.

e.g. `sudo apt-get install ttf-mscorefonts-installer`

## Usage

To generate the standard 94x94 icons and save them to the `static/icons/` directory, run:

python `generate_icons.py`

To set a different output location, set the `-o` parameter:

python `generate_icons.py -o OUTPUT_DIR`

To generate icons of a different size, set the `-s` parameter:

python `generate_icons.py -s SIZE`
