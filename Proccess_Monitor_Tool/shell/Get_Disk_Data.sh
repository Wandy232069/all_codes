#show parameter
function show_parameter {
	echo disk_loops = $loops
	echo disk_interval = $interval
	echo disk_path = $path
	echo disk_filename = $filename
}

show_parameter
date_format='%Y-%m-%d %H:%M:%S'
count=0
while [ $count -lt $loops ]
do
	echo -n "$(date +%Y-%m-%d\ %H:%M:%S), ">> $path$filename
	used_space=$(df -h | grep data | grep -v database | grep -v nvdata | grep -v aipc  | grep -v meta | grep -v mirror | awk '{print $5}')
	used_space="${used_space/\%/}"
	echo -n "$used_space," >> $path$filename
	echo -n "\n" >> $path$filename

  count=$((count+1))
  sleep $interval
done