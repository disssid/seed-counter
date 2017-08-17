#!/bin/bash

#rm ./logs/*
areaL=(200 400 600 800 1000 1200)
areaH=(8000 10000 12000 15000 18000 27000)
seed_type=("sesame-seeds" "wheat" "popcorn" "white-soya-beans" "red-seeds" "brown-seeds" "corn")
flow_rate=("normal" "fast")
i=0

while [ $i -le 6 ]
do
for element in ${areaL[@]}
do
	nohup python seedCount15Aug2017wheatTest2.py $element ${areaH[0]} ${seed_type[$i]} ${flow_rate[0]} > ./logs/areaL/${seed_type[$i]}-$element-${areaH[0]}-${flow_rate[0]}.log 2>&1 &
done

echo "Executing python programs for seed type "${seed_type[$i]}
echo -n "Progress : "
while pgrep -fl "seedCount15Aug2017wheatTest2.py" > /dev/null;
do 
	echo -n "#"
	sleep 2
done
echo
echo "Execution done"

d=$(date)
echo  >> full-report.log
echo "########################################################################" >> full-report.log
echo "#####################" $d "#####################" >> full-report.log
echo "########################################################################" >> full-report.log
grep "Number of seeds" logs/areaL/${seed_type[$i]}* >> full-report.log
grep "Average Area" logs/areaL/${seed_type[$i]}* >> full-report.log
echo "########################################################################" >> full-report.log
(( i++ ))
done
