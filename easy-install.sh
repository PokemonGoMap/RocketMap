#!/usr/bin/env bash
#
#  for even easier installation: copy-paste this line in your terminal (not the damn hash of course):
#  wget https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/develop/easy-install.sh && sudo chmod 755 easy-install.sh && bash ./easy-install.sh
#
# >>>  Created and tested on Ubuntu 16.04 64-bits <<<
#
# This script installs PokemonGo-Maps including the Hash-server configuration.
# It will prompt you for the install folder and the hash key, and when it's done, it's ready to use! 
# You need all prerequisits you 'normally' would need for PokemonGo-Maps. I will add a more comprehensive script that takes care
# of everything, so you could almost install it on a clean Ubuntu machine.
#
# >>> BY THE WAY: IT USES PYTON VIRTUAL ENVIRONMENT
# >>> what?!
# >>> simply said: it installs all python packages and stuff in the cloned folder, instead of using the (shared) system ones.
# >>> some people don't like that. Because it takes soooooooooooooo much space. but i do like it. 
# >>> because it installs and uses all packages dedicated for- and IN the application's folder, so less conflics IMHO.
# >>> also less free diskspace, that's the catch. 
# >>> PogoMaps will take around 190 Mb using Virtual Env. That's the size of a 10 minutes HD video. Wohooooo
# >>> Just take out line 47 if you don't like it. If you REALLY don't like it, take out line 56 too.
# 
#  > There are some useless or unusual functions.. also some explicit use of language. 
#  
#  > Sorry, that's the way *aha-aha* i like to write scripts :)  
# 
# * This is copyrighted material belonging to:
# The Beegees / song: Staying alive.
#
# Ah ah ah ah.. stayin aliiiiiiiiiiiiiiiive.
# Oops, i did it again.
# 
#
# (and now again)


BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

CREDITS="ULTRAFUNKAMSTERDAM"

	clear
	echo -e "\n\n\n====POKEMON GO MAPS SETUP ====\n\n\n"
	echo -e "Enter desired installation directory and make sure you have non-root access to that folder.\nJust press ENTER to install to /home/$USER/PokemonGo-Maps\n\n"
	read -p 'INSTALL DIR - FULL PATH ( default /home/$USER/PokemonGo-Maps/ )  :' INSTALLDIR
	[[ ! -z "$INSTALLDIR" ]] && mkdir $INSTALLDIR || INSTALLDIR=/home/$USER/PokemonGo-Maps
	echo -e "\n\n\nENTER YOUR HASH SERVER API KEY";
	read -p 'API KEY :' HASHAPIKEY
	echo -e -n "\n\nStarting installation" && for i in {10..30};do echo -e -n "." ;((i++));sleep 0.1;done
	clear


function virtualEnv(){
	[[ ! -z "$1" ]] && echo "I need no fucking param!";  
	cd $INSTALLDIR
	virtualenv .
	. bin/activate
}

git clone --recursive https://github.com/ultrafunkamsterdam/PokemonGo-Map-V2.git $INSTALLDIR
virtualEnv || { echo 'you need to install virtualenv for this to work (sudo apt-get install python-virtualenv)' ; exit $ERRCODE ; }
git checkout develop #just to be sure
pip install -r requirements.txt --upgrade
git submodule init && git submodule update
awk -v n=499 -v s="\t\tapi.activate_hash_server('$HASHAPIKEY')" 'NR == n {print s} {print}' pogom/search.py > search.tmp && mv search.tmp pogom/search.py
npm install && grunt build
deactivate
clear 
echo -e -n "\n\n\nINSTALLATION FINISHED ! Another script containing more fancyness than usable code, exlusively brought to you by:\n\n\t" && for i in {0..17}; do echo -e -n  "${CREDITS:i:1} " ;((i++));sleep 0.18; done  
echo -e "\n\n\nIMPORTANT!! : Don't forget to activate virtualenv before running runserver.py\nThis can be done by cd'ing into $INSTALLDIR and run:   . bin/activate   (DON'T FORGET THE DAMN DOT)\n\n\nOh, and when done, you can deactivate it anytime by just typing:  deactivate \n\n\nHAPPY CATCHING MOFO'S !! AND AH AH AHAH STAYING ALIVE!\n\n"
sleep 20

 
