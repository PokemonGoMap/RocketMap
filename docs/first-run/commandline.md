# Command Line

    usage: runserver.py [-h] [-cf CONFIG] [-a AUTH_SERVICE] [-u USERNAME]
                    [-p PASSWORD] [-ac ACCOUNTCSV] -w WORKERS -hk HASH_KEY -k
                    GMAPS_KEY -l LOCATION -st STEP_LIMIT [-gf GEOFENCE_FILE]
                    [-gef GEOFENCE_EXCLUDED_FILE] [--db-type {sqlite,mysql}]
                    [-D DB] [--db-name DB_NAME] [--db-user DB_USER]
                    [--db-pass DB_PASS] [--db-host DB_HOST]
                    [--db-port DB_PORT]
                    [--db-max_connections DB_MAX_CONNECTIONS]
                    [--db-threads DB_THREADS] [-np] [-nk] [-nr] [-ng | -gi]
                    [-ss [SPAWNPOINT_SCANNING] | -speed] [-bh]
                    [-wph WORKERS_PER_HIVE] [-kph KPH] [--skip-empty]
                    [-bsr BAD_SCAN_RETRY] [-msl MIN_SECONDS_LEFT]
                    [-sd SCAN_DELAY] [--spawn-delay SPAWN_DELAY] [-nj]
                    [-mf MAX_FAILURES] [-me MAX_EMPTY]
                    [-asi ACCOUNT_SEARCH_INTERVAL]
                    [-ari ACCOUNT_REST_INTERVAL] [-ld LOGIN_DELAY]
                    [-lr LOGIN_RETRIES] [-spin] [-ams ACCOUNT_MAX_SPINS]
                    [-enc] [-ed ENCOUNTER_DELAY] [-encwf ENC_WHITELIST_FILE]
                    [-hlvl HIGH_LVL_ACCOUNTS] [-hkph HLVL_KPH] [-nostore]
                    [-ns | -os] [-H HOST] [-P PORT] [-sc] [-nfl]
                    [--ssl-certificate SSL_CERTIFICATE]
                    [--ssl-privatekey SSL_PRIVATEKEY] [-C]
                    [-odt ON_DEMAND_TIMEOUT] [-al] [-L LOCALE] [-ps [logs]]
                    [-slt STATS_LOG_TIMER] [-sn STATUS_NAME]
                    [-spp STATUS_PAGE_PASSWORD] [-dc] [-wh WEBHOOKS]
                    [--wh-types {pokemon,gym,raid,egg,tth,gym-info,pokestop,lure}]
                    [--wh-threads WH_THREADS] [-whc WH_CONCURRENCY]
                    [-whr WH_RETRIES] [-wht WH_TIMEOUT]
                    [-whbf WH_BACKOFF_FACTOR] [-whlfu WH_LFU_SIZE]
                    [-wwht WEBHOOK_WHITELIST | -wblk WEBHOOK_BLACKLIST | -wwhtf WEBHOOK_WHITELIST_FILE | -wblkf WEBHOOK_BLACKLIST_FILE]
                    [-altv ALTITUDE_VARIANCE] [-uac] [-cs] [-ck CAPTCHA_KEY]
                    [-cds CAPTCHA_DSK] [-mcd MANUAL_CAPTCHA_DOMAIN]
                    [-mcr MANUAL_CAPTCHA_REFRESH]
                    [-mct MANUAL_CAPTCHA_TIMEOUT] [-px PROXY] [-pxsc]
                    [-pxt PROXY_TEST_TIMEOUT] [-pxre PROXY_TEST_RETRIES]
                    [-pxbf PROXY_TEST_BACKOFF_FACTOR]
                    [-pxc PROXY_TEST_CONCURRENCY] [-pxd {index,full}]
                    [-pxf PROXY_FILE] [-pxr PROXY_REFRESH]
                    [-pxo {none,round,random}] [-pd PURGE_DATA]
                    [--disable-clean] [-cd] [--dump-spawnpoints]
                    [--disable-blacklist] [-tp TRUSTED_PROXIES]
                    [--api-version API_VERSION] [-ldur LURE_DURATION] [-c]
                    [-m MOCK] [-apir API_RETRIES]
                    [-vci VERSION_CHECK_INTERVAL] [-v | --verbosity VERBOSE]
                    [--no-file-logs] [--log-path LOG_PATH]

Args that start with '--' (eg. -a) can also be set in a config file (/home/pokemad/pokemon/RocketMap/pogom/../config/config.ini or specified via -cf). The recognized syntax for setting (key, value) pairs is based on the INI and YAML formats (e.g. key=value or foo=TRUE). For full documentation of the differences from the standards please refer to the ConfigArgParse documentation. If an arg is specified in more than one place, then commandline values override config file values which override defaults.

### optional arguments

  -h, --help            show this help message and exit

### general

  -cf CONFIG, --config CONFIG
                        Set configuration file (default: None)
  -a AUTH_SERVICE, --auth-service AUTH_SERVICE
                        Auth Services, either one for all accounts or one per account: ptc or google. Defaults all to ptc. (default: [])
  -u USERNAME, --username USERNAME
                        Usernames, one per account. (default: [])
  -p PASSWORD, --password PASSWORD
                        Passwords, either single one for all accounts orone per account. (default: [])
  -ac ACCOUNTCSV, --accountcsv ACCOUNTCSV
                        Load accounts from CSV file containing "auth_service,username,passwd" lines. (default: None)
  -w WORKERS, --workers WORKERS
                        Number of search worker threads to start. (default: None)
  -hk HASH_KEY, --hash-key HASH_KEY
                        Key for hash server (default: None)
  -k GMAPS_KEY, --gmaps-key GMAPS_KEY
                        Google Maps Javascript API Key. (default: None)
  -l LOCATION, --location LOCATION
                        Location, can be an address or coordinates. (default: None)
  -st STEP_LIMIT, --step-limit STEP_LIMIT
                        Steps. (default: None)

### geofence

  -gf GEOFENCE_FILE, --geofence-file GEOFENCE_FILE
                        Geofence file to define outer borders of the scan area. (default: )
  -gef GEOFENCE_EXCLUDED_FILE, --geofence-excluded-file GEOFENCE_EXCLUDED_FILE
                        File to define excluded areas inside scan area. Regarded this as inverted geofence. Can be combined with geofence-file. (default: )

### database

  --db-type {sqlite,mysql}
                        Type of database to be used. (default: sqlite)
  -D DB, --db DB        Database filename for SQLite. (default: pogom.db)
  --db-name DB_NAME     Name of the database to be used. (default: None)
  --db-user DB_USER     Username for the database (MySQL). (default: None)
  --db-pass DB_PASS     Password for the database (MySQL). (default: None)
  --db-host DB_HOST     IP or hostname for the database (MySQL). (default: 127.0.0.1)
  --db-port DB_PORT     Port for the database (MySQL). (default: 3306)
  --db-max_connections DB_MAX_CONNECTIONS
                        Max connections for the database. (default: 5)
  --db-threads DB_THREADS
                        Number of db threads; increase if the db queue falls behind. (default: 1)

### map detail

  -np, --no-pokemon     Disables Pokemon from the map (including parsing them into local db.) (default: False)
  -nk, --no-pokestops   Disables PokeStops from the map (including parsing them into local db). (default: False)
  -nr, --no-raids       Disables Raids from the map (including parsing them into local db). (default: False)
  -ng, --no-gyms        Disables Gyms from the map (including parsing them into local db). (default: False)
  -gi, --gym-info       Get all details about gyms (causes an additional API hit for every gym). (default: False)
  -ignf IGNORELIST_FILE, --ignorelist-file IGNORELIST_FILE
                        File containing a list of Pokemon IDs to ignore, one line per ID. Spawnpoints will be saved, but ignored Pokemon  won't be encountered, sent to webhooks or saved to the DB. (default: )

### scheduler

  -ss [SPAWNPOINT_SCANNING], --spawnpoint-scanning [SPAWNPOINT_SCANNING]
                        Use spawnpoint scanning. Scans in a circle based on step_limit when on DB. (default: False)
  -speed, --speed-scan  Use speed scanning to identify spawn points and then scan closest spawns. (default: False)
  -bh, --beehive        Use beehive configuration for multiple accounts, one account per hex.  Make sure to keep -st under 5, and -w under the total amount of accounts available. (default: False)
  -wph WORKERS_PER_HIVE, --workers-per-hive WORKERS_PER_HIVE
                        Only referenced when using --beehive. Sets number of workers per hive (default: 1)
  -kph KPH, --kph KPH   Set a maximum speed in km/hour for scanner movement. (default: 35)
  --skip-empty          Enables skipping of empty cells in normal scans - requires previously populated database (not to be used with -ss) (default: False)
  -bsr BAD_SCAN_RETRY, --bad-scan-retry BAD_SCAN_RETRY
                        Number of bad scans before giving up on a step. 0 to disable. (default: 2)
  -msl MIN_SECONDS_LEFT, --min-seconds-left MIN_SECONDS_LEFT
                        Time that must be left on a spawn before considering it too late and skipping it. For example 600 would skip anything with < 10 minutes remaining. (default: 0)
  -sd SCAN_DELAY, --scan-delay SCAN_DELAY
                        Time delay between requests in scan threads. (default: 10)
  --spawn-delay SPAWN_DELAY
                        Number of seconds after spawn time to wait before scanning to be sure the Pokemon is there. (default: 10)
  -nj, --no-jitter      Don't apply random -9m to +9m jitter to location. (default: False)

### account management

  -mf MAX_FAILURES, --max-failures MAX_FAILURES
                        Maximum number of failures to parse locations before an account will go into a sleep for -ari/--account-rest-interval seconds. (default: 5)
  -me MAX_EMPTY, --max-empty MAX_EMPTY
                        Maximum number of empty scans before an account will go into a sleep for -ari/--account-rest-interval seconds.Reasonable to use with proxies. (default: 0)
  -asi ACCOUNT_SEARCH_INTERVAL, --account-search-interval ACCOUNT_SEARCH_INTERVAL
                        Seconds for accounts to search before switching to a new account. 0 to disable. (default: 0)
  -ari ACCOUNT_REST_INTERVAL, --account-rest-interval ACCOUNT_REST_INTERVAL
                        Seconds for accounts to rest when they put to sleep. (default: 7200)
  -ld LOGIN_DELAY, --login-delay LOGIN_DELAY
                        Time delay between each login attempt. (default: 6)
  -lr LOGIN_RETRIES, --login-retries LOGIN_RETRIES
                        Number of times to retry the login before refreshing a thread. (default: 3)
  -spin, --pokestop-spinning
                        Spin Pokestops with 50% probability. (default: False)
  -ams ACCOUNT_MAX_SPINS, --account-max-spins ACCOUNT_MAX_SPINS
                        Maximum number of Pokestop spins per hour. (default: 80)

### encounters

  -enc, --encounter     Start an encounter to gather IVs and moves. (default: False)
  -ed ENCOUNTER_DELAY, --encounter-delay ENCOUNTER_DELAY
                        Time delay between encounter pokemon in scan threads. (default: 1)
  -encwf ENC_WHITELIST_FILE, --enc-whitelist-file ENC_WHITELIST_FILE
                        File containing a list of Pokemon IDs to encounter for IV/CP scanning. (default: )
  -hlvl HIGH_LVL_ACCOUNTS, --high-lvl-accounts HIGH_LVL_ACCOUNTS
                        Load high level accounts from CSV file  containing "auth_service,username,passwd" lines. (default: None)
  -hkph HLVL_KPH, --hlvl-kph HLVL_KPH
                        Set a maximum speed in km/hour for scanner movement, for high-level (L30) accounts. (default: 25)
  -nostore, --no-api-store
                        Don't store the API objects used by the high level accounts in memory. This will increase the number of logins per account, but decreases memory usage. (default: False)

### web server

  -ns, --no-server      No-Server Mode. Starts the searcher but not the Webserver. (default: False)
  -os, --only-server    Server-Only Mode. Starts only the Webserver without the searcher. (default: False)
  -H HOST, --host HOST  Set web server listening host. (default: 127.0.0.1)
  -P PORT, --port PORT  Set web server listening port. (default: 5000)
  -sc, --search-control
                        Enables search control. (default: False)
  -nfl, --no-fixed-location
                        Disables a fixed map location and shows the search bar for use in shared maps. (default: True)
  --ssl-certificate SSL_CERTIFICATE
                        Path to SSL certificate file. (default: None)
  --ssl-privatekey SSL_PRIVATEKEY
                        Path to SSL private key file. (default: None)
  -C, --cors            Enable CORS on web server. (default: False)
  -odt ON_DEMAND_TIMEOUT, --on-demand_timeout ON_DEMAND_TIMEOUT
                        Pause searching while web UI is inactive for this timeout (in seconds). (default: 0)
  -al, --access-logs    Write web logs to access.log. (default: False)
  -L LOCALE, --locale LOCALE
                        Locale for Pokemon names (default: en, check static/dist/locales for more). (default: en)

### status/console

  -ps [logs], --print-status [logs]
                        Show a status screen instead of log messages. Can switch between status and logs by pressing enter.  Optionally specify "logs" to startup in logging mode. (default: False)
  -slt STATS_LOG_TIMER, --stats-log-timer STATS_LOG_TIMER
                        In log view, list per hr stats every X seconds (default: 0)
  -sn STATUS_NAME, --status-name STATUS_NAME
                        Enable status page database update using STATUS_NAME as main worker name. (default: 13437)
  -spp STATUS_PAGE_PASSWORD, --status-page-password STATUS_PAGE_PASSWORD
                        Set the status page password. (default: None)
  -dc, --display-in-console
                        Display Found Pokemon in Console. (default: False)

### webhooks

  -wh WEBHOOKS, --webhook WEBHOOKS
                        Define URL(s) to POST webhook information to. (default: None)
  --wh-types {pokemon,gym,raid,egg,tth,gym-info,pokestop,lure}
                        Defines the type of messages to send to webhooks. (default: [])
  --wh-threads WH_THREADS
                        Number of webhook threads; increase if the webhook queue falls behind. (default: 1)
  -whc WH_CONCURRENCY, --wh-concurrency WH_CONCURRENCY
                        Async requests pool size. (default: 25)
  -whr WH_RETRIES, --wh-retries WH_RETRIES
                        Number of times to retry sending webhook data on failure. (default: 3)
  -wht WH_TIMEOUT, --wh-timeout WH_TIMEOUT
                        Timeout (in seconds) for webhook requests. (default: 1.0)
  -whbf WH_BACKOFF_FACTOR, --wh-backoff-factor WH_BACKOFF_FACTOR
                        Factor (in seconds) by which the delay until next retry will increase. (default: 0.25)
  -whlfu WH_LFU_SIZE, --wh-lfu-size WH_LFU_SIZE
                        Webhook LFU cache max size. (default: 2500)
  -wwht WEBHOOK_WHITELIST, --webhook-whitelist WEBHOOK_WHITELIST
                        List of Pokemon to send to webhooks. Specified as Pokemon ID. (default: [])
  -wblk WEBHOOK_BLACKLIST, --webhook-blacklist WEBHOOK_BLACKLIST
                        List of Pokemon NOT to send to webhooks. Specified as Pokemon ID. (default: [])
  -wwhtf WEBHOOK_WHITELIST_FILE, --webhook-whitelist-file WEBHOOK_WHITELIST_FILE
                        File containing a list of Pokemon IDs to be sent to webhooks. (default: )
  -wblkf WEBHOOK_BLACKLIST_FILE, --webhook-blacklist-file WEBHOOK_BLACKLIST_FILE
                        File containing a list of Pokemon IDs NOT to be sent to webhooks. (default: )

### altitude

  -altv ALTITUDE_VARIANCE, --altitude-variance ALTITUDE_VARIANCE
                        Variance for altitude in meters (default: 1)
  -uac, --use-altitude-cache
                        Query the Elevation API for each step, rather than only once, and store results in the database. (default: False)

### captcha

  -cs, --captcha-solving
                        Enables captcha solving. (default: False)
  -ck CAPTCHA_KEY, --captcha-key CAPTCHA_KEY
                        2Captcha API key. (default: None)
  -cds CAPTCHA_DSK, --captcha-dsk CAPTCHA_DSK
                        Pokemon Go captcha data-sitekey. (default: 6LeeTScTAAAAADqvhqVMhPpr_vB9D364Ia-1dSgK)
  -mcd MANUAL_CAPTCHA_DOMAIN, --manual-captcha-domain MANUAL_CAPTCHA_DOMAIN
                        Domain to where captcha tokens will be sent. (default: http://127.0.0.1:5000)
  -mcr MANUAL_CAPTCHA_REFRESH, --manual-captcha-refresh MANUAL_CAPTCHA_REFRESH
                        Time available before captcha page refreshes. (default: 30)
  -mct MANUAL_CAPTCHA_TIMEOUT, --manual-captcha-timeout MANUAL_CAPTCHA_TIMEOUT
                        Maximum time captchas will wait for manual captcha solving. On timeout, if enabled, 2Captcha will be used to solve captcha. (default: 0)

### proxy

  -px PROXY, --proxy PROXY
                        Proxy url (e.g. socks5://127.0.0.1:9050) (default: None)
  -pxsc, --proxy-skip-check
                        Disable checking of proxies before start. (default: False)
  -pxt PROXY_TEST_TIMEOUT, --proxy-test-timeout PROXY_TEST_TIMEOUT
                        Timeout settings for proxy checker in seconds. (default: 5)
  -pxre PROXY_TEST_RETRIES, --proxy-test-retries PROXY_TEST_RETRIES
                        Number of times to retry sending proxy test requests on failure. (default: 0)
  -pxbf PROXY_TEST_BACKOFF_FACTOR, --proxy-test-backoff-factor PROXY_TEST_BACKOFF_FACTOR
                        Factor (in seconds) by which the delay until next retry will increase. (default: 0.25)
  -pxc PROXY_TEST_CONCURRENCY, --proxy-test-concurrency PROXY_TEST_CONCURRENCY
                        Async requests pool size. (default: 0)
  -pxd {index,full}, --proxy-display {index,full}
                        Display info on which proxy being used. To be used with -ps. (default: index)
  -pxf PROXY_FILE, --proxy-file PROXY_FILE
                        Load proxy list from text file (one proxy per line), overrides -px/--proxy. (default: None)
  -pxr PROXY_REFRESH, --proxy-refresh PROXY_REFRESH
                        Period of proxy file reloading, in seconds. Works only with -pxf/--proxy-file. (0 to disable). (default: 0)
  -pxo {none,round,random}, --proxy-rotation {none,round,random}
                        Enable proxy rotation with account changing for search threads. (default: round)

### database maintenance

  -pd PURGE_DATA, --purge-data PURGE_DATA
                        Clear Pokemon from database this many hours after they disappear (0 to disable). (default: 0)
  --disable-clean       Disable clean db loop. (default: False)
  -cd, --clear-db       Deletes the existing database before starting the Webserver. (default: False)
  --dump-spawnpoints    Dump the spawnpoints from the db to json (only for use with -ss). (default: False)

### anti scrappers (web server)
  --disable-blacklist   Disable the global anti-scraper IP blacklist. (default: False)
  -tp TRUSTED_PROXIES, --trusted-proxies TRUSTED_PROXIES
                        Enables the use of X-FORWARDED-FOR headers to identify the IP of clients connecting through these trusted proxies. (default: [])

### others

  --api-version API_VERSION
                        API version currently in use. (default: 0.69.1)
  -ldur LURE_DURATION, --lure-duration LURE_DURATION
                        Change duration for lures set on pokestops. This is useful for events that extend lure duration. (default: 30)
  -c, --china           Coordinates transformer for China. (default: False)
  -m MOCK, --mock MOCK  Mock mode - point to a fpgo endpoint instead of using the real PogoApi, ec: http://127.0.0.1:9090 (default: )
  -apir API_RETRIES, --api-retries API_RETRIES
                        Number of times to retry an API request. (default: 3)
  -vci VERSION_CHECK_INTERVAL, --version-check-interval VERSION_CHECK_INTERVAL
                        Interval to check API version in seconds (use 0 to disable). (default: 269)

### debug
  -v                    Show debug messages from RocketMap and pgoapi. Can be repeated up to 3 times. (default: 0)
  --verbosity VERBOSE   Show debug messages from RocketMap and pgoapi. (default: None)
  --no-file-logs        Disable logging to files. Does not disable --access-logs. (default: False)
  --log-path LOG_PATH   Defines directory to save log files to. (default: logs/)
