# Configuration files

Configuration files can be used to organize server/scanner deployments.  Any long-form command-line argument can be specified in a configuration file.

##  Default file

The default configuration file is *config/config.ini* underneath the project home. However, this location can be changed by setting the environment variable POGOMAP_CONFIG or using the -cf or --config flag on the command line. In the event that both the environment variable and the command line argument exists, the command line value will take precedence. Note that all relative pathnames are relative to the current working directory (often, but not necessarily where runserver.py is located).  The recognized syntax for setting (key, value) pairs is based on the INI and YAML formats (e.g. key=value or foo=TRUE).

##  Example Config file

There is a default example configuration file underneath the project home in /config/config.ini.example.  This file contains many of the most common options that can be set in a configuration file, followed by a comment explaining what the option does.  Note that for editing the ini files that the # symbol prefaces a comment, meaning anything after it on the line is ignored.  As the file notes, please use a proper editor such as NotePad++.  Remember to "Save As" after, and ensure the config file is saved as an ini.

## Setting configuration key/value pairs

  For command line values that take a single value they can be specified as:

    keyname: value
    e.g.   host: 0.0.0.0

  For parameters that may be repeated:

    keyname: [ value1, value2, ...]
    e.g.   username: [ randomjoe, bonnieclyde ]

  For command line arguments that take no parameters:

    keyname: True
    e.g.   fixed-location: True

## Example config file

  <pre>
  -- contents of file myconfig.seattle --
  username: [ randomjoe, bob ]
  password: [ password1, password2 ]
  location: seattle, wa
  step-limit: 5
  gmaps-key: MyGmapsKeyGoesHereSomeLongString
  print-status: True
  -- end of file --
  </pre>

  Running this config file as:

     python runserver.py -cf myconfig.seattle

  would be the same as running with the following command line:

     python runserver.py -u randomjoe -p password1 -u bob -p password2 -l "seattle, wa" -st 5 -k MyGmapsKeyGoesHereSomeLongString -ps
     
##  List of Possible Flags     

## Running multiple configs

   One common way of running multiple locations is to use two configuration files each with common or default database values, but with different location specs. The first configuration running as both a scanner and a server, and in the second configuration file, use the *no-server* flag to not start the web interface for the second configuration.   In the config file, this would mean including a line like:

   no-server: True
