for i in `seq 0 34`; do
	str="screen -x pkmn-worker${i}-thread -X kill"
	eval $str
done
