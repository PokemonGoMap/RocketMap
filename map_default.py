#!/usr/bin/env python

# This program is pretty raw, but it open map.common.js in an array
# then it reads the map-defaults file and merges them.
# Finally, writes the map.common.js back.
# Then when the grunt build process begins, the customizations
# are included

# Some options are integers, others are string.
# This will be used to differentiate between them

option_type = {}
config_opts = {}

option_type['map_style'] = 'text'
option_type['remember_select_exclude'] = 'array'
option_type['remember_select_notify'] = 'array'
option_type['remember_select_rarity_notify'] = 'array'
option_type['remember_select_exclude'] = 'array'
option_type['remember_text_perfection_notify'] = 'text'
option_type['remember_select_exclude'] = 'array'
option_type['playSound'] = 'boolean'
option_type['showPokestops'] = 'boolean'
option_type['showPokemon'] = 'boolean'
option_type['showGyms'] = 'boolean'
option_type['startAtUserLocation'] = 'boolean'
option_type['zoomLevel'] = 'integer'

mapjs = "static/js/map.common.js"
map_defaults = "config/map-defaults.ini"


def read_config():
    file_dict = {}
    raw_contents = open(map_defaults).readlines()
    for line in raw_contents:
        # build a dictionary of settings and values
        if not line.startswith("#") and not line.startswith("\n"):
            # split up the line, using the colon dilimeter
            (setting, value) = line.rstrip().split(":")
            file_dict[setting] = value.lstrip()
    return file_dict


def main():
    mapjs_arr = open(mapjs).readlines()
#    for line in mapjs_arr:
#        print line,
    config_dict = read_config()
    # loop through the file array and compare it to the hash key of options
    for i in range(len(mapjs_arr)):
        for key, value in config_dict.iteritems():
            if key in mapjs_arr[i]:
                # line next line should be 'default'.
                # But we can't guarantee it hasn't been modified
                # So we need to look for it.
                for j in range(i, len(mapjs_arr)):
                    if "default" in mapjs_arr[j]:
                        # build a new string now, but base it on
                        # the old one to keep the formatting.
                        new_line = mapjs_arr[j].split(":")[0]
                        # now format it based on the type
                        if option_type[key] == 'text':
                            mapjs_arr[j] = new_line + ": '" + value + "',\n"
                        if option_type[key] == 'array':
                            mapjs_arr[j] = new_line + ": " + value + ",\n"
                        if option_type[key] == 'boolean':
                            mapjs_arr[j] = new_line + ": " + value + ",\n"
                        if option_type[key] == 'integer':
                            mapjs_arr[j] = new_line + ": " + value + ",\n"
                        break
    # Now write the file out
    mapjs_out = open(mapjs, 'w')
    for line in mapjs_arr:
        mapjs_out.write(line)
    mapjs_out.close()


if __name__ == "__main__":
    main()
