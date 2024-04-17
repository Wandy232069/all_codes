#kill exist CPU monitor
for PID in `ps -ef | grep qa_CPU_monitor | grep -v grep |grep -v awk | awk '/qa_CPU_monitor/ {print $2}'`; do kill -9 $PID ; done

cd /data/local/tmp/qa

nohup ./qa_CPU_monitor.sh 2>&1 &

exit