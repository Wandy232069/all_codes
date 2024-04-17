# !/system/bin/sh

#these parameter will be appended in SAW_TT.SAWui.trigger_monitor
#interval, loops

#default on logs
storagelog=1

#default off logs
detailstoragelog=0

#show parameter
function show_parameter {
	echo disk_loops = $loops
	echo disk_interval = $interval
	echo disk_log = $storagelog
	echo detail_disk_log = $detailstoragelog
}

show_parameter

echo -n "Time," > qa_DISK_monitor.csv
if [ $storagelog == 1 ]; then
	echo -n "Storage Used," >> qa_DISK_monitor.csv
fi
echo "" >> qa_DISK_monitor.csv
#exit


count=0
while [ $count -lt $loops ]
do
	echo -n "$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_DISK_monitor.csv
	
	if [ $storagelog == 1 ]; then
		used_space=$(df -h | sed -n '2p' | awk '{print $5}')
		used_space="${used_space/\%/}"
		echo -n "$used_space," >> qa_DISK_monitor.csv
	fi
	echo "" >> qa_DISK_monitor.csv

	# output detailed CPU to qa_detail_storage.log
	if [ $detailstoragelog == 1 ]; then
		echo -e "\n\n====$(date +%Y-%m-%d\ %H:%M:%S), " >> qa_detail_storage.log
		df -a >> qa_detail_storage.log
	fi

    count=$((count+1))
    sleep $interval
done