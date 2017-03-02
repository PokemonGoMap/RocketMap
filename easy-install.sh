#!/usr/bin/env bash
#
#  for even easier installation: copy-paste this line in your terminal (not the damn hash of course):

# [[ -f easy-install.sh ]] && rm easy-install.sh ; wget https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/MASTER/easy-install.sh && sudo chmod 755 easy-install.sh && bash ./easy-install.sh

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
	echo -e "THIS IS IMPORTANT: \n\n" 
	echo -e "You are no longer required to type your BossLand Hashkey in here, instead use it like:"
	echo -e "python ./runserver.py -hk YOURKEY -hk YOURKEY2 -hk YOURKEY ( rest of configuration )\n"
	echo -e "For more information about command line options please visit:\nhttps://github.com/ultrafunkamsterdam/PokemonGo-Map-V2/blob/develop/pogom/utils.py#L54-L224 \n\n"
	read -p 'INSTALL DIR - FULL PATH ( default /home/'$USER'/PokemonGo-Maps )  :' INSTALLDIR
    read -p 'Name of your maps? (Will substitute "Rocket Maps" to your desired name) :' MAPSNAME
	[[ ! -z "$INSTALLDIR" ]] && mkdir $INSTALLDIR || INSTALLDIR=/home/$USER/PokemonGo-Maps
	#echo -e "\n\n\nENTER YOUR HASH SERVER API KEY";
	#read -p 'API KEY :' HASHAPIKEY
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
git checkout rpm #just to be sure
git submodule init && git submodule update
pip install -r requirements.txt
command -v unzip >/dev/null 2>&1 || ( echo -e "Unzip is needed for the static assets to unzip ... \n" && sleep 2 && echo -e "Trying to install ... \n" && sudo apt-get install unzip; if [ $? -eq 0 ] ; then echo "Successfully installed!"; else echo "Error installing unzip. Exiting ..." && exit -1;fi ) 
wget https://github.com/ultrafunkamsterdam/PokemonGo-Map-V2/raw/develop/static.zip
unzip -o static.zip
if [ $? -ge 1 ]; then 
echo -e "Unzipping failed! Exiting script now ... \n" && sleep 2 && exit -1
else 
echo -e "Unzipping completed successfully, proceeding to build static assets ... \n" && sleep 2
fi
[[ ! -z $MAPSNAME ]] && sed -i "s|Rocket Map|$MAPSNAME|g" templates/*
npm install
deactivate
clear 
echo -e -n "\n\n\nINSTALLATION FINISHED ! Another script containing more fancyness than usable code, exlusively brought to you by:\n\n\t" && for i in {0..17}; do echo -e -n  "${CREDITS:i:1} " ;((i++));sleep 0.18; done  
echo -e "\n\n\nIMPORTANT!! : Don't forget to activate virtualenv before running runserver.py\nThis can be done by cd'ing into $INSTALLDIR and run:   . bin/activate   (DON'T FORGET THE DAMN DOT)\n\n\nOh, and when done, you can deactivate it anytime by just typing:  deactivate \n\n\nHAPPY CATCHING MOFO'S !! AND AH AH AHAH STAYING ALIVE!\n\n"
sleep 20

 
