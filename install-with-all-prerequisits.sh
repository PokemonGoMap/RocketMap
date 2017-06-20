#!/usr/bin/env bash
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
clear
#
# FOR EASY INSTALLATION USING 1 LINE. COPY BELOW LINE AND PASTE IT IN YOUR TERMINAL (DO NOT COPY THE HASH PLEASE).
# [[ -f install-with-all-prerequisits.sh ]] && rm install-with-all-prerequisits.sh; wget https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/develop/install-with-all-prerequisits.sh ; sudo chmod 775 install-with-all-prerequisits.sh && bash ./install-with-all-prerequisits.sh
#
echo -e "\n\n\t======= This will install everything you need in order to install and run PokemonGo-Maps =======\n\n"
#echo -e "\n\n\tYou should run this script with sudo privileges:  sudo bash $0 \nIf yo " 
echo -e "\n\n\tThere will be some packages removed using this script (nodejs-legacy nodejs nodered npm) and replaced by a newer version\n\tIf you are on v6 already, it will skipp automatically"

echo -e -n "\t"; read -n 20 -s -p "Press any key to continue, (or wait 20 seconds) : "

#echo -e "\n\n\tpress ctrl+c to cancel . I'll give you 10 seconds to copy above command to and press ctrl+C to cancel\
# this. After that, script will start running and giving lots of errors." && sleep 10
echo -e -n "\n\n\tStarting installation" && for i in {10..30};do echo -e -n "." ;((i++));sleep 0.1;done
echo -e "\n\n\tThere we go!!! Jihaaaaa" && sleep 4
clear

sudo apt-get -y update 
echo -e "--------------\n\tPackagemanager updated!\n\t" 
sleep 3
clear
# LIBWWW-CURL-PERL
sudo apt-get install -y libwww-curl-perl 
echo -e "--------------\n\tlibwww-curl-perl installed!\n\t" 
sleep 3
clear

# REMOVING OLD VERSIONS OF NODE, NPM NODERED 
sudo apt-get -y purge nodejs nodejs-legacy nodered npm
echo -e "--------------\n\tOld versions of node and npm removed!\n\t" 
sleep 3
clear

# INSTALL OLDER NODE BACK AGAIN (SOME BUG)


# NPM NODE MORE RECENT STUFF
curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
sudo apt-get install -y nodejs

echo -e "--------------\n\tNew version(6.x) of node and npm installed! Including legacy!\n\t" 
sleep 3
clear

#PYTHON
sudo apt-get install -y python2.7 python-pip python-dev python-virtualenv git
echo -e "--------------\n\tInstalled python 2.7 python-pip python-dev python-virtualenv git!\n\t" 
sleep 3
clear


echo -e "Let's check version of NPM. Should be 3.10.x \n\n"
npm -v 
sleep 3
clear
sudo npm install -g grunt-cli
echo -e "--------------\n\tGrunt-cli installed!\n\t" 
sleep 3
clear

sleep 2
clear
echo -e "\n\tDONE INSTALLING PREREQUISITS" && sleep 4
echo -e "\n\tNow we are going to install PokemonGo-Map with Hash Server support." && sleep 4
echo -e -n "\n\n\tHERE WE GO AGAIN!" && for i in {10..30};do echo -e -n "." ;((i++));sleep 0.1;done

[[ -f pogomapsinstaller.sh ]] && rm -f pogomapsinstaller.sh
wget https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/develop/pogomapsinstaller.sh && sudo chmod 755 pogomapsinstaller.sh
bash ./pogomapsinstaller.sh


