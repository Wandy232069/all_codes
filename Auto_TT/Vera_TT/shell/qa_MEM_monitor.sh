#!/bin/bash

#define variable set default parameter
#interval=1800
#loops=144

#default on logs
memorylog=1

#default off logs
detailmemorylog=0

function PrintLogHeader(){
	for process in ${processArray[@]}
	do
		now=$(date)
		process_name=$(echo "$process" | tr -d '()')
		echo Time,"Memory %" >> qa_${process_name}_MEM.csv
	done
}

#show parameter
function show_parameter {
	echo loops = $loops
	echo interval = $interval
	echo memorylog = $memorylog
	echo detailmemorylog = $detailmemorylog
}

total_mem=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}') 

show_parameter
PrintLogHeader "$process"

echo -n "Time," > qa_MEM_monitor.csv
if [ $memorylog == 1 ]; then
	echo -n "Memory Usage," >> qa_MEM_monitor.csv
fi
echo "" >> qa_MEM_monitor.csv
#exit

count=0
while [ $count -lt $loops ]
do
	echo -n "$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_MEM_monitor.csv
	
	if [ $memorylog == 1 ]; then
		mem=$(free -m | sed -n '2p' | awk '{printf("%.2f\n", $3/$2 * 100)}')
		echo -n "$mem," >> qa_MEM_monitor.csv
	fi
	echo "" >> qa_MEM_monitor.csv

	# output detailed CPU to qa_detail_memory.log
	if [ $detailmemorylog == 1 ]; then
		echo -e "\n\n====$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_detail_memory.log
		free >> qa_detail_memory.log
		echo -e "\n\n" >> qa_detail_memory.log
		ps -A -o user,pid,%CPU,%mem,vsz,rss,tty,stat,time,command >> qa_detail_memory.log
	fi

	for process in ${processArray[@]}
	do
		process_id=$(vlcm list | grep ${process} | awk '{print $3}')
		process_name=$(echo "$process" | tr -d '()')
		
		if [ -z "$process_id" ]; then
			echo ${process}" is not running" >> qa_${process_name}_MEM.csv

		else
			echo "$(date +%Y-%m-%d\ %H:%M:%S), $(perf_data_collector -p ${process_id} -i 1 -d 0.1 | sed -n 's/{.*"pss":\[//p' | sed -n 's/,.*//p' | sed 's/.*]/,/g' | sed -n 's/\[*. //p' | awk '{printf "%.2f", $1 / '${total_mem}' * 100}') " >> qa_${process_name}_MEM.csv &
		fi
		
	done

    count=$((count+1))
    sleep $interval
done