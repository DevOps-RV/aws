#!/bin/bash
# Source the domain.properties file
. /home/oracle/OSService_WLS/domain.properties

source $setDomainEnv
sh $wlst $serverstate
#java weblogic.WLST $serverstate
