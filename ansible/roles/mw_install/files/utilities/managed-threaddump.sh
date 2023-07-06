#!/bin/bash

#Interval in seconds between data points.
INTERVAL=30

counter=1

# Export  Java Home
JAVA_HOME=/opt/oracle/jdk

#host=uname -a | awk '{print $2}'
host=$HOSTNAME
SERVERDUMP_LOCATION=/opt/oracle/backup/threaddump
TODAY_DATE=$(date +"%d%m%Y_%H%M%S")


#create Server Dumps directory
if [ ! -d ${SERVERDUMP_LOCATION} ]
then
echo "creating dump directory"
mkdir $SERVERDUMP_LOCATION
fi

PID=${pgrep -f mserver -n}

# read input
if [ -z $PID ]; then
  # process id is  empty
  echo "Run the command in the format: sh thread"
  exit 1
fi


while [ $counter -le 3 ]
do
  echo "*****Generating Thread dump #" $counter
  $JAVA_HOME/bin/jstack -l $PID >> $SERVERDUMP_LOCATION/managed_threaddump_$TODAY_DATE.out
  counter=$(( $counter + 1 ))
  sleep $INTERVAL
done

echo "Done *****"

