This tool pulls a list of Pokestops from the Database, teleports a scanner account to each one, gets the Pokestop information and stores them in the DB
This wont look very human, so dont use with an important account.

Example usage:

python getPokestopDetails.py -u my_test_usr -p supersecretpass -l 'town' --db-type mysql -px socks5://localhost:9050 --db-name pokemongomap --db-user pkm --db-pass pkm
