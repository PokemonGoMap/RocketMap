#!/bin/bash
#see https://github.com/AHAAAAAAA/PokemonGo-Map/wiki

STEPS=4
POSITIONS=(
	#"account:ptc:${STEPS}:lat/long"
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
		
		str="screen -AmdS pkmn-worker${i}-thread python runserver.py --no-server -st ${steps} -a ${auth} -u ${login} -p password -l \"${pos}\"";
	
		echo "executing '${str}'"
		eval $str
	fi
	
	i=$((i + 1))
done
