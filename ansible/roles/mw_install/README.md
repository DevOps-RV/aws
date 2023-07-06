# SOA, OSB, AIA, OSM, ODI 12.2.1.4v

Oracle Weblogic Application Deployment 

## Getting Started
```
Prereq: Install Users, Rpm's, Oracle Client and JDK on all servers
Oracle Fusion Middleware Binaries: Infra, WLS and Binaries (SOA, OSB, AIA, OSM, ODI) for MW SUITE Installation on all nodes.
Install Required Patches
RCU and Domain and Admin Server Installation and Pack on the First node in the inventory group provided
Install Managed Server using unpack on all nodes with Performance configuration
Delete Medec Server after complete installation
AIA - AntFIX, Domain Update, O2C deploy, Pack and Unpack
Update Load Balancer URL
Node Manager Password Update (Prereq for init.d)
Integrate init.d


```

### Prerequisites
```
Update the ansible inventory with the new hosts in hosts.ini
Update Passwords in vars/groupvars
AIA - OracleBRMJCA15Adapter.rar should be present for ENV's in artifactory
AIA - Update BRM and SBL details in the group vars, BRM and SBL needs to be up
AIA - cwallet.sso, ewallet.p12 needs to be in wallet
if the parameters in aia_run_config response file has special characters, it needs to be use with escpae character \
example: SBL_DB_PSWD: password123#
   echo -n 'password123#' | base64
   T3JhY2xlMTJcIw==
   SBL_DB_PSWD={{ SBL_DB_PSWD | b64decode }}
```
### Installing
```

Role Variables Used

    SUITE: Select the Middleware Suite
    ENV: Select the Middleware Environment
    MW_HOSTS: Select the Inventory Group Name
    INSTALLATION_TYPE: Select the installation type. for END-to-END installation select "all"	
    DB_NAME: Select DB Name. 
    DB_HOST_NAME: select DB Hostname or FQDN. 
    DB_PORT: Enter the DB Port Number. Default 1521
    DOMAIN_NAME: select Domain Name. 
    RCU_SCHEMA_PREFIX: Select the RCU Prefix. 
    CLUSTER_NAME: Select the Cluster Name. 	
    LOCAL_LOAD_BALANCER: HTTP for given Datacenter
    MW_ADMIN_PORT: Enter Middleware Admin Server Port Number	
    MS_PORT: Enter Middleware Managed Server Port Number	
    LIMIT_HOST (optional):  Enter The HOST Name or Group as in Inventory to Limit operations to that node/group	
    DEBUG (optional): Ansible Verbose -v,-vv or -vvv

Tags Used - Installation Type

    prechecks: to Verify server requirements
    prereqs: will install rpms, setup folders and permissions, oracle client, jdk and download binaries
    check_vars: To Verify all Variables declared for RCU, Domain installation, and Pack
    all: Complete END - END Installation
    jdk: Install JDK on all Nodes
    binary_install: Install WLS, Infra and Suite Binaries on all nodes
    rcu: Install RCU components from node1
    domain: Install Domain on node1
    pack: Pack domain and push to artifactory
    domain_backup: Backup Domain
    ms_unpack: Unpack Managed Server and start on all nodes
    medrec_delete: Delete Sample Medrec Server. Eg: soa_server1, osb_server1
    aia_antfix:
    aia_domain_update: 
    aia_o2c_deploy: 
    aia_unpack:
    lb_update: Load Balancer Configuration
    nm_pass_update: Node Manager Password Update ( PreReq for init.d)
    init: init.d service scripts integration for start/stop/restart
    patch: Install Required Patches

```
CLEAN UP - OSM:
drop user "OSMORDER" CASCADE;
drop user "OSMORDER_REPORTS" CASCADE;
drop user "OSMORDER_RULE" CASCADE;
drop user OSM_WLS CASCADE;
drop user OSM_WLS_RUNTIME CASCADE;
# drop TABLESPACE OSB; #optional

Example Playbook
----------------

OSB Installation
```
ansible-playbook playbooks/mw_install.yml -t binary_install,rcu,domain,pack,ms_unpack -e SUITE=OSB
```

License
-------

BSD

Author Information
------------------
Raghu Vamsi
