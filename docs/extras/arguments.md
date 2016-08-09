# Command Line Arguments

Args that start with '--' (eg. -a) can also be set in a config file (../config/config.ini).  
The recognized syntax for setting (key, value) pairs is based on the INI and YAML formats (e.g. key=value or foo=TRUE). For full documentation of the differences from the standards please refer to the ConfigArgParse documentation. If an arg is specified in more than one place, then commandline values override config file values which override defaults.

## Optional arguments:

- **-h, --help**: show the help message and exit
- **-a AUTH_SERVICE, --auth-service AUTH_SERVICE**:  Auth Services, either one for all accounts or one per account. ptc or google. Defaults all to ptc.
- **-u USERNAME, --username USERNAME**: Usernames, one per account.
- **-p PASSWORD, --password PASSWORD**: Passwords, either single one for all accounts or one per account.
- **-l LOCATION, --location LOCATION**: Location, can be an address or coordinates
- **-st STEP_LIMIT, --step-limit STEP_LIMIT**: Steps
- **-sd SCAN_DELAY, --scan-delay SCAN_DELAY**: Time delay between requests in scan threads default 10
- **-ld LOGIN_DELAY, --login-delay LOGIN_DELAY**: Time delay between each login attempt default is 5
- **-dc, --display-in-console**:  Display Found Pokemon in Console
- **-H HOST, --host HOST**: Set web server listening host
- **-P PORT, --port PORT**: Set web server listening port
- **-L LOCALE, --locale LOCALE**: Locale for Pokemon names (default: en, check static/dist/locales for more)
- **-c, --china**: Coordinates transformer for China
- **-d, --debug**: Debug Mode
- **-m, --mock**: Mock mode. Starts the web server but not the background thread.
- **-ns, --no-server**: No-Server Mode. Starts the searcher but not the Webserver.
- **-os, --only-server**: Server-Only Mode. Starts only the Webserver without the searcher.
- **-nsc, --no-search-control**: Disables search control
- **-fl, --fixed-location** Hides the search bar for use in shared maps.
- **-k GMAPS_KEY, --gmaps-key GMAPS_KEY** Google Maps Javascript API Key
- **-C, --cors**: Enable CORS on web server
- **-D DB, --db DB**: Database filename
- **-cd, --clear-db**: Deletes the existing database before starting the Webserver.
- **-np, --no-pokemon**: Disables Pokemon from the map (including parsing them into local db)
- **-ng, --no-gyms**: Disables Gyms from the map (including parsing them into local db)
- **-nk, --no-pokestops**: Disables PokeStops from the map (including parsing them into local db)
- **--db-type DB_TYPE**: Type of database to be used (default: sqlite)
- **--db-name DB_NAME**: Name of the database to be used
- **--db-user DB_USER**: Username for the database
- **--db-pass DB_PASS**: Password for the database
- **--db-host DB_HOST**: IP or hostname for the database
- **--db-max_connections DB_MAX_CONNECTIONS**: Max connections for the database
- **-wh [WEBHOOKS [WEBHOOKS ...]], --webhook [WEBHOOKS [WEBHOOKS ...]]**: Define URL(s) to POST webhook information to