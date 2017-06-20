#!/usr/bin/env bash
#
#=========*=========*=========*=========*=========*
#   PokemonGo-Map installer from scratch. This is the only file you need !
#   Author : UltrafunkAmsterdam
#   https://www.github.com/UltrafunkAmsterdam
#=========*=========*=========*=========*=========*
#
#   install.sh  |  IMPORTANT : READ THIS FIRST!
#    
#   This script is meant to be run stand-alone! You do NOT need to clone this repo first. You can download just this file and execute it.
#   You should download the raw file and not the url of the current page!!! 
#   download: https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/updateRM/pogomapsinstaller.sh
#   You can specify what PokemonGo-Maps Repository you want below this block. 
#   Added awesome new sprites, much better then those ugly default sprites. Check them out at https://pokemaplive.nl or here
#   https://raw.githubusercontent.com/ultrafunkamsterdam/PokemonGo-Map-V2/flat-icons/static/flat-sh-tr-icons-large-sprite.png
#   The icons will be added by default, and if you do not want to use them, you should modify static/map.common.js and set :
#   var flaticons = false;    default (true)
# 

  
  REPOURL="https://github.com/ultrafunkamsterdam/PokemonGo-Map-V2"  ## or https://github.com/RocketMap/RocketMap
  BRANCH="0.63.1"  ## choose life choose a job choose a career choose a family, choose branch!  (for rocketmap set to "develop")
  PID=$$
 
  THISPATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
  PARENTPATH="${0%/*}"
  MYNAME="${0##*/}"
 
  Time(){ date "+%H:%M:%S";}
  Date(){ date "+%d-%m-%y";}
  TimeStamp(){ echo -e -n "$(Date) $(Time)";}
  SL(){ sleep $1;}
  n(){ echo -e "\n";}
 
   
  Re='\e[0m'
  Bla='\e[0;30m';     BBla='\e[1;30m';    UBla='\e[4;30m';    IBla='\e[0;90m';    BIBla='\e[1;90m';   On_Bla='\e[40m';    On_IBla='\e[0;100m';
  Red='\e[0;31m';     BRed='\e[1;31m';    URed='\e[4;31m';    IRed='\e[0;91m';    BIRed='\e[1;91m';   On_Red='\e[41m';    On_IRed='\e[0;101m';
  Gre='\e[0;32m';     BGre='\e[1;32m';    UGre='\e[4;32m';    IGre='\e[0;92m';    BIGre='\e[1;92m';   On_Gre='\e[42m';    On_IGre='\e[0;102m';
  Yel='\e[0;33m';     BYel='\e[1;33m';    UYel='\e[4;33m';    IYel='\e[0;93m';    BIYel='\e[1;93m';   On_Yel='\e[43m';    On_IYel='\e[0;103m';
  Blu='\e[0;34m';     BBlu='\e[1;34m';    UBlu='\e[4;34m';    IBlu='\e[0;94m';    BIBlu='\e[1;94m';   On_Blu='\e[44m';    On_IBlu='\e[0;104m';
  Pur='\e[0;35m';     BPur='\e[1;35m';    UPur='\e[4;35m';    IPur='\e[0;95m';    BIPur='\e[1;95m';   On_Pur='\e[45m';    On_IPur='\e[0;105m';
  Cya='\e[0;36m';     BCya='\e[1;36m';    UCya='\e[4;36m';    ICya='\e[0;96m';    BICya='\e[1;96m';   On_Cya='\e[46m';    On_ICya='\e[0;106m';
  Whi='\e[0;37m';     BWhi='\e[1;37m';    UWhi='\e[4;37m';    IWhi='\e[0;97m';    BIWhi='\e[1;97m';   On_Whi='\e[47m';    On_IWhi='\e[0;107m';
   
  Logger(){
    PRETTYNAME="PogoMaps Install"
    LOGTYPE="$1"
    MESSAGE="$2"
    #Logger Templates
    DISP_TITLE="${BIWhi}${On_Pur}  $PRETTYNAME  ${Re}${IWhi}${On_Cya} $MESSAGE ${Re}"
    DISP_INFO_STYLE="${BIWhi}[$PRETTYNAME][INFO] : $MESSAGE ${Re}"
    DISP_WARN_STYLE="${BIWhi}[$PRETTYNAME][${Re}${BIYel}WARNING${Re}${BIWhi}] : $MESSAGE ${Re}"
    DISP_ERROR_STYLE="${BIWhi}[$PRETTYNAME][${BIRed}ERROR${Re}${BIWhi}] : $MESSAGE ${Re}"
    DISP_SUCCESS_STYLE="${BIWhi}[$PRETTYNAME][${BIGre}SUCCESS${Re}${BIWhi}] : $MESSAGE ${Re}"
    LOGFILE_STYLE="[$PRETTYNAME][$(TimeStamp)][${LOGTYPE^^}] : $MESSAGE "
    #Logger Logic
    [[ ! -z ${LOGTYPE} ]] && [[ -z ${MESSAGE} ]] && echo -e "${BIWhi}[$PRETTYNAME] : $LOGTYPE ${Re}" && return 0
    [[ -z $LOGTYPE ]] && echo -e "${BIWhi}${On_Red} Logger () : First argument missing ( Log type ) ${Re}"
    [[ -z $MESSAGE ]] && echo -e "${BIWhi}${On_Red} Logger () : Second argument missing ( Message ) ${Re}"
    [[ ${LOGTYPE^^} == "TITLE" ]] && echo -e "$DISP_TITLE"  
    [[ ${LOGTYPE^^} == "WARN" ]] && echo -e "$DISP_WARN_STYLE"  
    [[ ${LOGTYPE^^} == "ERROR" ]] && echo -e "$DISP_ERROR_STYLE"
    [[ ${LOGTYPE^^} == "SUCCESS" ]] && echo -e "$DISP_SUCCESS_STYLE"
    [[ ${LOGTYPE^^} == "INFO" ]] && echo -e "$DISP_INFO_STYLE"
    [[ ${LOGTYPE^^} == "LOGFILE" ]] &&  while read -r RAW; do MESSAGE="$RAW" && echo -e "$LOGFILE_STYLE" >> $LOGFILE ;done
    return 0
  }
 
  Usage()
  {
    Logger title " Usage & Debug "
    Logger "Arguments : $ARGS_ARRAY"
    Logger "Path to this script from caller : ${0}"
    Logger "Path to this script (full) : $BASE_DIR/$0"
    Logger "Parent folder : ${0%/*}"
    Logger "My name : ${0##*/}"
    Logger title "USAGE"
    Logger "Make sure you install it in your home drive so you do not need sudo, just for convenience and easy-ness"
    Logger "$0"
  }
 
  StopSelf()
  {
    Logger info "Thank you for using $PRETTYNAME" && SL 2
    kill -9 $$
    exit 1
  }
 
  CheckOS()
  {
    distro=$(lsb_release -ds 2>/dev/null || cat /etc/*release 2>/dev/null | head -n1 || uname -om)
    which yum &>/dev/null && install="sudo yum -y install " && remove="sudo yum -y remove "
    which zyppe &>/dev/null && install="sudo zypper -n install " && remove="sudo zypper -y remove "
    which apt-get &>/dev/null && install="sudo apt-get -y install " && remove="sudo apt-get -y remove --purge "
   
    return 0
  }
 
  NOTINSTALLED=()
  ReqMan()
  {
    [[ -z "$1" ]] && Logger error "Requirements checker : Argument missing [install] [remove]" && StopSelf
      action="$1"
    shift
   
    if [[ "${action^^}" == "CHECK" ]]; then
       
        [[ -f applist ]] || sudo apt list -qq > applist 2>&1
        for x in "$@"
        do
            grep -io -q "$x" applist && Logger success "$x is currently installed" || ( Logger warn "$x is currently not installed" && NOTINSTALLED=("${NOTINSTALLED[@]}" "$x") )
        done
        rm -f applist >/dev/null
       
    fi
       
    [[ "${action^^}" == "REMOVE" ]] && for x in "$@"; do ${remove} "$x" ; done
    [[ "${action^^}" == "INSTALL" ]] && for x in "$@"; do ${install} "$x" ; done  
  }
 
   
  ReceivedExit(){
    clear
    echo -e "\n"
    Logger title " Termination signal received "
    Logger warn "Received ctrl+c or other interruption signal "
    Logger info "Stopping ... "
    StopSelf && exit
  }
 
  Init(){
    trap ReceivedExit SIGHUP SIGINT SIGTERM EXIT
    touch ${THISPATH}/foo >/dev/null && rm -f ${THISPATH}/foo || Logger "error" "Folder has incorrect permissions! Please make it writeable by the current user"
    CheckOS
  }
 
  function VirtualEnv(){
    [[ ! -z "$1" ]] && echo "I need no fucking param!";  
    cd $INSTALLDIR
    virtualenv .
    . bin/activate
  }
 
  Main(){
    clear
    echo -e "\n"
    Logger title " WELCOME [ https://github.com/ultrafunkamsterdam ] "
    echo -e "${BWhi} \n" && SL 2
    Logger info "Checking all requirements first .. "
   
    ReqMan "check" "curl" "perl" "mysql-client" "mysql-server"
   
    if node -v | grep -E "^v6" >/dev/null ;then
        Logger success "NodeJS is is currently installed";
    else
        Logger info "Updating NodeJS .. "
        curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
        sudo apt-get install -y nodejs
        #curl -sL https://deb.nodesource.com/setup_6.x >/dev/null | sudo -E bash - >/dev/null
        ReqMan install nodejs
    fi
   
    ReqMan check nodejs-legacy python2.7 python-pip python-dev python-setuptools python-virtualenv git
    if npm --version | grep -io -E '^3'  ; then sudo npm install -g grunt-cli >/dev/null ; else Logger warn "NPM version is outdated! .. : $(npm --version)" ; fi
    read -p 'INSTALL DIR - FULL PATH ( default /home/'$USER'/PokemonGo-Maps )  :' INSTALLDIR ; SL 2
    read -p 'Name of your maps? (Will substitute "Rocket Maps" to your desired name) :' MAPSNAME ; SL 2
    [[ ! -z "$INSTALLDIR" ]] && mkdir $INSTALLDIR || INSTALLDIR=/home/$USER/PokemonGo-Maps ; SL 2
    git clone --recursive $REPOURL $INSTALLDIR ; SL 2
    VirtualEnv || { echo 'you need to install virtualenv for this to work (sudo apt-get install python-virtualenv)' ; exit $ERRCODE ; }
    git checkout "$BRANCH" ; SL 2
    git submodule init && git submodule update ; SL 2
    pip install -r requirements.txt
    ReqMan check unzip wget
    wget https://github.com/ultrafunkamsterdam/PokemonGo-Map-V2/raw/develop/static.zip
    wget https://github.com/ultrafunkamsterdam/PokemonGo-Map-V2/raw/develop/staticicons.zip
    unzip -o static.zip
    unzip -o staticicons.zip
    if [ $? -ge 1 ]; then
    echo -e "Unzipping failed! Exiting script now ... " ; SL 2 ; exit -1
    else
    echo -e "Unzipping completed successfully, proceeding to build static assets .. " && SL 2
    fi
    [[ ! -z $MAPSNAME ]] && sed -i "s|Rocket Map|$MAPSNAME|g" templates/* static/*
    rm -f static.zip &>/dev/null
    rm -f static01.zip &>/dev/null
    npm install && SL 2
    deactivate
    clear
  }

   
Init && Main && StopSelf
