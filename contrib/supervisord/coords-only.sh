#!/bin/bash

# Using this until they allow location_generator.py to allow coords only mode!

output="coords.txt"   # Name of the coords file
lat="29.882687"       # Latitiude
lon="-97.94071"       # Longitude
st="5"                # Steps
lp="6"                # Leaps
dir="/opt/pokegomap/" # Path to main Pokemon Go Map folder. NOTE THE TRAILING /

# Runs location_generator.py with info from above, outputs to a caca file after taking out
# the top line "Generating yadayada" and places it neatly where we want supervisord to see it
/usr/bin/python "$dir"Tools/Hex-Beehive-Generator/location_generator.py -lat $lat -lon $lon \
-st $st -lp $lp -o caca -v | sed '/Generating/d' > ~/supervisor/$output

# Get rid of caca beehive file
rm caca
