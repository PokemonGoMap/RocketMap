for i in `seq 0 60`; do
	str="screen -x pkmn-worker${i}-thread -X kill"
	eval $str
done
