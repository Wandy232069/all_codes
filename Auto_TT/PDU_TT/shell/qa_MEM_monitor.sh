# !/system/bin/sh

#these parameter will be appended in SAW_TT.SAWui.trigger_monitor
# interval,loops, processArray

#default on logs
memorylog=1

#default off logs
detailmemorylog=0



function PrintLogHeader(){
	for process in ${processArray[@]}
	do
		now=$(date)
		echo Time,Memory,pid,args>> qa_${process}_MEM.csv
	done
}


#show parameter
function show_parameter {
	echo memory_loops = $loops
	echo memory_interval = $interval
	echo memory_log = $memorylog
	echo detail_memory_log = $detailmemorylog
}


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
#		mem=$(free -m | sed -n '2p' | awk '{printf("%.2f\n", $3/$2 * 100)}')
    mem=$(top -b -n 1 | grep Mem | grep -v grep | awk '{print $4/$2*100}')
		echo -n "$mem," >> qa_MEM_monitor.csv
	fi
	echo "" >> qa_MEM_monitor.csv

	# output detailed CPU to qa_detail_memory.log
	if [ $detailmemorylog == 1 ]; then
		echo -e "\n\n====$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_detail_memory.log
		free >> qa_detail_memory.log
		echo -e "\n\n" >> qa_detail_memory.log
		ps -aux >> qa_detail_memory.log
	fi

	for process in ${processArray[@]}
		do
		# special case to handle "com.mobiledrivetech.smartclock" and "com.mobiledrivetech.smartclocksettings"
		  time=$(date +%Y-%m-%d\ %H:%M:%S)
			if [ "$process" == "com.mobiledrivetech.smartclock" ]; then
			  top -b -n 1 | grep ${process} | grep -v "com.mobiledrivetech.smartclocksettings" | grep -v grep | grep -v sh  | awk '{OFS=", ";print $10,$1,$12}'| sed -e 's/^/'"$time, "'/g'  >> qa_${process}_MEM.csv
			else
        top -b -n 1 | grep ${process}  | grep -v grep | grep -v sh  | awk '{OFS=", ";print $10,$1,$12}' | sed -e 's/^/'"$time, "'/g' >> qa_${process}_MEM.csv
			fi
		done

    count=$((count+1))
    sleep $interval
done