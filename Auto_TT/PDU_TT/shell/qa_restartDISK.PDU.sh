#kill exist MemCpuMon
for PID in `ps -ef | grep qa_DISK_monitor | grep -v grep |grep -v awk | awk '/qa_DISK_monitor/ {print $2}'`; do kill -9 $PID ; done

cd /data/local/tmp/qa

nohup ./qa_DISK_monitor.sh 2>&1 &

exit 