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

  For parameters that may be repeated (usernames, passwords, black/whitelists, hashkeys):

    keyname: [ value1, value2, ...]
    e.g.   username: [ randomjoe, bonnieclyde ]

  For command line arguments that take no parameters:

    keyname: True
    e.g.   fixed-location: True

## Example config file

  See the file in the config directory named **config.ini.example**.  This file contains a list of all the commands that can be set in configuration files.  Remember that the arguments specified on the commandline will over-ride an option in the config file.

  Running this config file from the commandline using the -cf configuration flag:

     python runserver.py -cf config/config.ini.example
      
##  List of Possible Flags     

See the **config.ini.example** or the [Command Line Documentation](https://rocketmap.readthedocs.io/en/develop/extras/commandline.html) in this wiki.  You can also find them in the python code in the pogom directory in **utils.py**

## Running multiple configs

   One common way of running multiple locations is to use multiple configuration files each with common or default database values, but with different location specs. The first configuration running as a **server**(with -os flag), and in the second configuration file, use the **no-server**(with -ns flag) to not start the web interface for any other configuration.   
   
   In the first config file, this would mean including a line like:
        
    `only-server: true`
    

    In the second config file, this would mean including a line like:
        
    `no-server: true`

