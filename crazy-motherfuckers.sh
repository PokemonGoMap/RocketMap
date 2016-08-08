#!/bin/bash
#see https://github.com/AHAAAAAAA/PokemonGo-Map/wiki

STEPS=4
POSITIONS=(
	"JapuDKroete:ptc:${STEPS}:51.51059,7.46315"				#Stadtgarten
	"JapuDKloete:ptc:${STEPS}:51.5129427,7.4715866"			#Olpe
	"JapuDCaterer:ptc:${STEPS}:51.51166,7.46826"			#Vapiano
	"JapuDKoeter:ptc:${STEPS}:51.5138027,7.4659274"			#alter Markt
	"Marvindon@web.de:google:${STEPS}:51.5138027,7.4659274"	#alter Markt, Google
	"JapuDKreter:ptc:${STEPS}:51.514099,7.4598509"			#Thier-Gallerie
	"JapuDPeter:ptc:${STEPS}:51.5165347,7.4583002"			#Hbf
	"JapuDMeter:ptc:${STEPS}:51.516265,7.4687257"			#Netto
	
	"JapuDInterpreter:ptc:${STEPS}:51.5092897,7.4693693"	#Stadthaus
	"JapuDLepra:ptc:${STEPS}:51.5034427,7.4723016"			#Stadewaeldchen
	"JapuDPetra:ptc:${STEPS}:51.5035871,7.4666982"			#Ruhrallee
	"JapuDKrater:ptc:${STEPS}:51.5053787,7.459614"			#Telekom
	
	"JapuDKater:ptc:${STEPS}:51.4945072,7.4183501"			#FH
	"JapuDKatze:ptc:${STEPS}:51.4919086,7.4104627"			#TU
	"JapuDAder:ptc:${STEPS}:51.48915,7.50072"				#Hoerde
	"JapuDKadse:ptc:${STEPS}:51.49116,7.50662"				#Phoenixsee-West
	"JapuDReder:ptc:${STEPS}:51.48866,7.51806"				#Phoenixsee-Ost
	"JapuDRaeder:ptc:${STEPS}:51.48911,7.51112"				#Phoenixsee-Mitte
	"JapuDCater:ptc:${STEPS}:51.5116076,7.4805719"			#Kaiserstraße
	
	"JapuDCarter:ptc:${STEPS}:51.5249725,7.4850192"			#Borsigplatz
	"JapuDVaeter:ptc:${STEPS}:51.52639,7.46285"				#Nordmarkt
	"JapuDKratze:ptc:${STEPS}:51.5218463,7.4598062"			#Nordbad
	
	"JapuDKretze:ptc:7:51.5959525,7.4405203"				#Brambauer
	"JapuDKotze:ptc:9:51.5186168,7.5441669"					#Brackel
	"JapuDHetze:ptc:${STEPS}:51.504354,7.493578"			#Materna
	"JapuDHexe:ptc:${STEPS}:51.5071238,7.4652889"			#Sonnenstraße
	"JapuDMixer:ptc:${STEPS}:51.5121172,7.450976"			#Westpark-Sued
	"JapuDMetzger:ptc:${STEPS}:51.5075136,7.4511036"		#Moellerbruecke
	"JapuDFetzer:ptc:${STEPS}:51.5035460,7.4518559"			#Kreuzviertel
	"JapuDHaxor:ptc:7:51.496531,7.476607"					#Westfalenpark
	"JapuDRotze:ptc:5:51.5559141,7.9133944"					#Werl-Mitte
	"JapuDVerraeter:ptc:${STEPS}:51.55327,7.91217"			#Werl-Mitte2
	"JapuDMotze:ptc:5:51.5659224,7.9071091"					#Werl-Nord
	"JapuDSpaeter:ptc:${STEPS}:51.56061,7.91777"			#Werl-Ost
	"JapuDKaka:ptc:5:51.5485583,7.9161267"					#Werl-Sued
	
	#"JapuDMader:ptc:${STEPS}:"
	#"JapuDRader:ptc:${STEPS}:"
)

position_length=10
regex="(.*):(.*):(.*):(.*)"
i=0

for p in "${POSITIONS[@]}"; do
	if [[ $p =~ $regex ]]
	then
		login="${BASH_REMATCH[1]}"
		auth="${BASH_REMATCH[2]}"
		steps="${BASH_REMATCH[3]}"
		pos="${BASH_REMATCH[4]}"
		
		str="screen -AmdS pkmn-worker${i}-thread python runserver.py --no-server -st ${steps} -a ${auth} -u ${login} -p sleeper89 -l \"${pos}\"";
	
		echo "executing '${str}'"
		eval $str
	fi
	
	i=$((i + 1))
done