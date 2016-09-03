for i in `seq 0 30`; do
	str="screen -x pkmn_worker${i}-thread -X kill"
	eval $str
done
