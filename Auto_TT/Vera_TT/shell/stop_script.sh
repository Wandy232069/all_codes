#!/bin/bash
for PID in `ps -ef | grep qa_MEM_monitor | grep -v grep |grep -v awk | awk '/qa_MEM_monitor/ {print $2}'`; do kill -9 $PID ; done
for PID in `ps -ef | grep qa_CPU_monitor | grep -v grep |grep -v awk | awk '/qa_CPU_monitor/ {print $2}'`; do kill -9 $PID ; done
for PID in `ps -ef | grep qa_DISK_monitor | grep -v grep |grep -v awk | awk '/qa_DISK_monitor/ {print $2}'`; do kill -9 $PID ; done