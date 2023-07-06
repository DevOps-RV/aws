########################################################################################
# BRM JCA Adapter Update Automation WLST Script                                        #                                                                    #
# Restart the servers after running this script.                                       #
#Do not change the description                                                         #
########################################################################################
#Running the script                                                                    #
########################################################################################
#WL_HOME\server\bin\setWLSEnv.cmd or                                                   #
#source $WL_HOME/server/bin/setWLSEnv.sh                                               #
#java weblogic.WLST <Folder_Loc>/deployBRMJCATest.py                                   #
########################################################################################

from java.io import FileInputStream
import java.lang
import string
import sys
#read properties file
propInputStream = FileInputStream("BRMResourceAdapter.properties");
configProps = Properties();
configProps.load(propInputStream);
#Connecting to Server
adminusername = configProps.get('ADMIN_USERNAME');
adminpassword = configProps.get('ADMIN_PASSWORD');
adminurl = configProps.get('ADMIN_URL');
clusterName = configProps.get('CLUSTER_NAME');
connect(adminusername, adminpassword, adminurl)
domainName=cmo.getName();
serverList = cmo.getServers();
server1=serverList[1].getName();
appName              = configProps.get('appName');
moduleOverrideName   = appName+'.rar'
moduleDescriptorName = configProps.get('moduleDescriptorName');
def __undeployBRMJCAAdapter():
 edit();
 startEdit();
 print 'Undeploying BRM JCA Adapter'
 undeploy(appName);
 activate();
 planFile = configProps.get('planFile');
 os.remove(planFile)
 
def createDeploymentPlanVariable(wlstPlan, name, value, xpath, origin='planbased'):
#Create a variable in the Plan.
#This method is used to create the variables that are needed in the Plan.xml file
##
 
 try:  
    variableAssignment = wlstPlan.createVariableAssignment(name, moduleOverrideName, moduleDescriptorName)
    variableAssignment.setXpath(xpath)
    variableAssignment.setOrigin(origin)
    wlstPlan.createVariable(name, value)
 except:
    print('--> was not able to create deployment plan variables successfully') 
 
def __deployBRMJCAAdapter():
 eisName = configProps.get('eisName');
 BRMConnectionPoolTimeout = configProps.get('BRMConnectionPoolTimeout')
 ConnectionString = configProps.get('ConnectionString')
 BRMConnectionPoolMaxsize = configProps.get('BRMConnectionPoolMaxsize')
 AverageOpcodeCount = configProps.get('AverageOpcodeCount')
 MultiDB = configProps.get('MultiDB')
 ZeroEpochAsNull = configProps.get('ZeroEpochAsNull')
 BRMConnectionPoolMinsize = configProps.get('BRMConnectionPoolMinsize')
 transactionMode = configProps.get('transactionMode')
 rarLocation = configProps.get('rarLocation')
 print 'Deploying BRM JCA Adapter'
 cd('Servers')
 edit();
 startEdit();
 deploy(appName, rarLocation, targets=clusterName, createPlan='true')
 activate();
#
# update the deployment plan
#
 print('--> about to update the deployment plan for the Adapter')
 edit();
 startEdit();
 planPath = get('/AppDeployments/'+appName+'/PlanPath')
 appPath = get('/AppDeployments/'+appName+'/SourcePath')
 print('--> Using plan ' + planPath)
 plan = loadApplication(appPath, planPath)
 print('--> adding variables to plan')
 createDeploymentPlanVariable(plan, 'ConfigProperty_BRMConnectionPoolTimeout_Value_1',BRMConnectionPoolTimeout, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="BRMConnectionPoolTimeout"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_ConnectionString_Value_2', ConnectionString, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="ConnectionString"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_BRMConnectionPoolMaxsize_Value_3', BRMConnectionPoolMaxsize, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="BRMConnectionPoolMaxsize"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_AverageOpcodeCount_Value_4', AverageOpcodeCount, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="AverageOpcodeCount"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_MultiDB_Value_5', MultiDB, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="MultiDB"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_ZeroEpochAsNull_Value_6', ZeroEpochAsNull, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="ZeroEpochAsNull"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_BRMConnectionPoolMinsize_Value_7', BRMConnectionPoolMinsize, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="BRMConnectionPoolMinsize"]/value')
 createDeploymentPlanVariable(plan, 'ConfigProperty_transactionMode_Value_8', transactionMode, '/weblogic-connector/outbound-resource-adapter/connection-definition-group/[connection-factory-interface="oracle.tip.adapter.api.OracleConnectionFactory"]/connection-instance/[jndi-name="' + eisName + '"]/connection-properties/properties/property/[name="transactionMode"]/value')
 print('--> saving plan')
 plan.save();
 cd('/AppDeployments/'+appName+'/Targets');
 print('--> redeploying the OracleBRMJCA15Adapter')
 updateApplication(appName, planPath);
 print('--> activating changes')
 print('--> done')
 activate(block='true');
 
# MAIN
#****************************************************************************
#
# Calling all the Methods here
print(' ————————– ')
print('Starting the changes')
print('#########################################################################################################################')
#print 'Do you want to undeploy BRM JCA Adapter'
#input = raw_input("Press y to PROCEED or press n to SKIP ===================================================>                          ");
#if input == 'y':
# __undeployBRMJCAAdapter()
  
#print 'Do you want to deploy BRM JCA Adapter'
#input = raw_input("Press y to PROCEED or press n to SKIP ===================================================>                          ");
#if input == 'y':
__deployBRMJCAAdapter()
#else:
# exit();