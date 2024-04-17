# !/system/bin/sh

#these parameter will be appended in SAW_TT.SAWui.trigger_monitor
#interval,loops, processArray

#default on logs
cpulog=1


#default off logs
detailcpulog=0


function PrintLogHeader(){
	for process in ${processArray[@]}
	do
		now=$(date)
		echo Time,CPU,pid,args>> qa_${process}_CPU.csv
	done
}

#show parameter
function show_parameter {
	echo cpu_loops = $loops
	echo cpu_interval = $interval
	echo cpu_log = $cpulog
	echo detail_cpu_log = $detailcpulog
}

show_parameter
PrintLogHeader "$process"

echo -n "Time," > qa_CPU_monitor.csv
if [ $cpulog == 1 ]; then
	echo -n "CPU Loading," >> qa_CPU_monitor.csv
fi
echo "" >> qa_CPU_monitor.csv
#exit


count=0
while [ $count -lt $loops ]
do
	echo -n "$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_CPU_monitor.csv

	if [ $cpulog == 1 ]; then
		cpu_load=$(top -b -n 1 | grep -e %cpu | grep -v grep | awk '{print ($1-$5)}')
		echo -n "$cpu_load" >> qa_CPU_monitor.csv
	fi
	echo "" >> qa_CPU_monitor.csv

	for process in ${processArray[@]}
		do
		# special case to handle "com.mobiledrivetech.smartclock" and "com.mobiledrivetech.smartclocksettings"
		time=$(date +%Y-%m-%d\ %H:%M:%S)
			if [ "$process" == "com.mobiledrivetech.smartclock" ]; then
			  top -b -n 1 | grep  ${process} | grep -v "com.mobiledrivetech.smartclocksettings" | grep -v grep | grep -v sh | awk '{OFS=", ";print $9,$1,$12}' | sed -e 's/^/'"$time, "'/g' >>  qa_${process}_CPU.csv
			else
				top -b -n 1 | grep  ${process} | grep -v grep | grep -v sh  | awk '{OFS=", ";print $9,$1,$12}' | sed -e 's/^/'"$time, "'/g' >>  qa_${process}_CPU.csv
			fi
		done

    count=$((count+1))
    sleep $interval
done