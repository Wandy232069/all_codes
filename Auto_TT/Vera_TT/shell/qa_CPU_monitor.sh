#!/bin/bash

#define variable set default parameter
#interval=1800
#loops=144

#default on logs
cpulog=1

#default off logs
detailcpulog=0

# Create process folder
function PrintLogHeader(){
	for process in ${processArray[@]}
	do
		process_name=$(echo "$process" | tr -d '()')
		echo Time,CPU % >> qa_${process_name}_CPU.csv
	done
}

#show parameter
function show_parameter {
	echo loops = $loops
	echo interval = $interval
	echo cpulog = $cpulog
	echo detailcpulog = $detailcpulog
}

show_parameter
PrintLogHeader "$process"

echo -n "Time," > qa_CPU_monitor.csv
if [ $cpulog == 1 ]; then
	echo -n "CPU Loading," >> qa_CPU_monitor.csv
fi
echo "" >> qa_CPU_monitor.csv

count=0
while [ $count -lt $loops ]
do
	echo -n "$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_CPU_monitor.csv
	
	if [ $cpulog == 1 ]; then
		cpu_total=$(cat /proc/stat | grep '^cpu ' | awk '{print $2+$3+$4+$5+$6+$7+$8}')
		cpu_idle=$(cat /proc/stat | grep '^cpu ' | awk '{print $5}')
		cpu_used=$(expr $cpu_total - $cpu_idle)
		cpu_load=$(expr $cpu_used \* 100 / $cpu_total)
		echo -n "$cpu_load," >> qa_CPU_monitor.csv
	fi
	echo "" >> qa_CPU_monitor.csv
	
	# output detailed CPU to qa_detail_cpu.log
	if [ $detailcpulog == 1 ]; then
		echo -e "\n\n====$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_detail_cpu.log
		top -bn1 >> qa_detail_cpu.log
	fi

	for process in ${processArray[@]}
	do
		process_id=$(vlcm list | grep ${process} | awk '{print $3}')
		process_name=$(echo "$process" | tr -d '()')
		
		if [ -z "$process_id" ]; then
			echo ${process}" is not running" >> qa_${process_name}_CPU.csv
		else
			echo "$(date +%Y-%m-%d\ %H:%M:%S), $(perf_data_collector -p ${process_id} -i 1 -d 0.1 | sed -n 's/{.*"co":\[//p' | sed -n 's/,.*//p' | sed 's/.*]/,/g' | sed -n 's/\[*. //p') " >> qa_${process_name}_CPU.csv &
		fi		
	done	
    count=$((count+1))
    sleep $interval
done