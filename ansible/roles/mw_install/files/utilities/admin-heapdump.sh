#!/bin/sh

# Export  Java Home
JAVA_HOME=/opt/oracle/jdk

host=$HOSTNAME
SERVERDUMP_LOCATION=/opt/oracle/backup/heapdump
TODAY_DATE=$(date +"%d%m%Y")

#create Server Dumps directory
if [ ! -d ${SERVERDUMP_LOCATION} ]
then
echo "creating dump directory"
mkdir $SERVERDUMP_LOCATION
fi

PID=$(pgrep -f AdminServer)

if [ -z $PID ]; then
  # process id is  empty
  echo "provide JVM PID"
  exit 1
fi

echo "*****Geneating Heap dump  ***"

$JAVA_HOME/bin/jmap -J-d64 -dump:format=b,file=$SERVERDUMP_LOCATION/heapdump/Admin_heapdump_$TODAY_DATE.hprof $PID

