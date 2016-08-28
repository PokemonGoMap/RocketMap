## Fresh Start ##
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 600 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000 
Start "Worker 600" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x600.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 700 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 700" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x700.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 800 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 800" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x800.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 900 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 900" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x900.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 200 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 200" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x200.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 300 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 300" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x300.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 400 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 400" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x400.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

## Worker 500 ###
Start "Web Server" /d C:\PokemonMap2 /MIN C:\Python27\Python.exe C:\PokemonMap2\runserver.py -os -l "60.391027, 5.326085" -fl -nsc --db-max_connections 1000
Start "Worker 500" /d C:\PokemonMap2 C:\Python27\Python.exe C:\PokemonMap2\runserver.py -ns -ps -j -ss spawns.json -configfile config\config.x500.ini
ping 127.0.0.1 -n 10800 > nul
taskkill /f /im python.exe
ping 127.0.0.1 -n 4 > nul

start C:\PokemonMap2\StartServer.bat