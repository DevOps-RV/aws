#!/bin/bash
LC=`/sbin/ifconfig -a | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}' | tr "\n" "|"`dsdf
netstat -an | grep tcp | awk '{if($5 !~ /:[0-9][0-9][0-9][0-9][0-9]/){print $5}}' | sort | uniq | egrep -v $LC | awk -F: '{CMD="nslookup "$1" | grep name | cut -f2 -d="; CMD | getline A ; print A ":" $2}
' >> /tmp/ntfloHN_`hostname`.txt
netstat -an | grep tcp | awk '{if($5 !~ /:[0-9][0-9][0-9][0-9][0-9]/){print $5}}' | sort | uniq | egrep -v $LC >> /tmp/ntfloIP_`hostname`.txt

