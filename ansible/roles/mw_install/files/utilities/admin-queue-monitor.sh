#!/bin/bash
#

funMWServerCheck ()
{
		CNT=`df -Ph  | awk '{if(NR==1){print $0} else {per=substr($5, 0, length($5)-1);   if(int(per) >= 80){print $0}}}' | wc -l`
        if [ $CNT -gt 1 ]
        then
                DSKUSAGE="YELLOW"
        else
                DSKUSAGE="GREEN"
        fi

        TOPC=`top -b -n1 | grep -e "^%Cpu" -e "^KiB Swap" -e "^Cpu" -e "^Swap" |  tr "n" "," | awk -F, '{print $4 }' | awk '{print substr($0,1,3)}'| tail -1`
        CPUSTAT=`echo $TOPC | awk '{if($1 < 60 ){print "GREEN";}if($1 >= 60 && $1 <= 80){print "YELLOW";}if($1 > 80){print "RED"}}'`

        TSWAP=`free -m | grep Swap | awk '{print $2}'`
        FSWAP=`free -m | grep Swap | awk '{print $4}'`

        if [ $TSWAP -ne $FSWAP ]
        then
                FREESWAPPCNT=`echo $FSWAP "," $TSWAP | awk -F, '{print ($1/$2)*100}'`
                SWAPSTAT=`echo $FREESWAPPCNT |  awk '{if($1 < 70 ){print "RED";}if($1 >= 70 && $1 <= 90){print "YELLOW";}if($1 > 90){print "GREEN"}}'`
        else
                SWAPSTAT="GREEN"
        fi

        WCOUNT=`cat /opt/scripts/status.log | grep "^[a-z,A-Z]" | grep -v OK | wc -l `
        if [ $WCOUNT == "0" ]
        then
                SERVSTAT="GREEN"
        else
                SERVSTAT="YELLOW"
        fi
        SCOUNT=`cat /opt/scripts/status.log | grep "^[a-z,A-Z]" | grep -v RUNNING | wc -l `
        if [ $SCOUNT != "0" ]
        then
                SERVSTAT="RED"
        fi

        sh /opt/scripts/fd-monitor.sh
        if [ `cat /opt/scripts/fd-output.log` == "TRUE" ]; then FDSTAT="RED"; else FDSTAT="GREEN"; fi
		
	sh /opt/scripts/fd-monitor.sh
	if [ `cat /opt/scripts/fd-output.log` == "TRUE" ]; then FDSTAT="RED"; else FDSTAT="GREEN"; fi
	QSTAT="N/A"
	if [ `cat /opt/scripts/queue-status.log | grep -i RED | wc -l ` -ge 1 ]; then QSTAT="YELLOW"; else QSTAT="GREEN"; fi
        #echo -e "Server name t Disk status t Memory status t CPU status t Servers status t FD status t Error-Queues-Depth"
        echo -e `hostname -s`,$DSKUSAGE,$SWAPSTAT,$CPUSTAT,$SERVSTAT,$FDSTAT,$QSTAT
}
funMWServerCheck

