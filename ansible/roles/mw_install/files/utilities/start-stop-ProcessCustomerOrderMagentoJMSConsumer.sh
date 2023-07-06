#!/bin/bash

WLST_HOME=/opt/oracle/fmw12214/oracle_common/common/bin/
SCRIPT_HOME=/opt/oracle/scripts

source $WLST_HOME/setWlstEnv.sh
java weblogic.WLST $SCRIPT_HOME/start-stop-ProcessCustomerOrderMagentoJMSConsumer.py $1