
# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands
```
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
```
Enjoy!


###For Testing
```
* export CDK_DEPLOY_REGION=us-east-2 
* export CDK_DEFAULT_ACCOUNT=123456789

* CDK_DEPLOY_REGION=us-east-2 cdk ls --context stackDirectory=/stacks/dev --context stackName=AuroraMysqlStack
* CDK_DEPLOY_REGION=us-east-2 cdk diff --context stackDirectory=/stacks/dev --context stackName=AuroraMysqlStack
* CDK_DEPLOY_REGION=us-east-2 cdk synth --context stackDirectory=/stacks/dev --context stackName=AuroraMysqlStack
* CDK_DEPLOY_REGION=us-east-2 cdk deploy --context stackDirectory=/stacks/dev --context stackName=AuroraMysqlStack
```

## CDK | RDS | Aurora-MySql Parameters

### Config Common Parameters
```
  existing_security_groups: [dev-oh-rds-sg1,dev-oh-rds-sg2] #sg names
  existing_subnets: [dev-ec2-us-east-2a,dev-ec2-us-east-2b,dev-ec2-us-east-2c] #ec2 subnet names
  kms_key_alias: rds-kms-key #kms key alias name
  secret_rotation_lambda_name: rds-creds-rotate-test

  #create a subnet group with above existing subnets
  db_subnet_group_name: dev-oh-rds-sng
```
###  Mandatory DB Parameters
```
mysql_clusters:
    db_cluster_identifier: dev-aurora-mysql-cluster1 #Name of the  cluster
    family: aurora-mysql8.0 #aws rds describe-db-engine-versions --query "DBEngineVersions[].DBParameterGroupFamily
    engine_version: 8.0.mysql_aurora.3.02.0 #https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Updates.Versions.html
    db_engine_mode: provisioned #The serverless engine mode only supports Aurora Serverless v1. Currently, AWS CloudFormation doesn't support Aurora Serverless v2.
    cluster_parameter_group_values:
      'time_zone': 'UTC'
      'performance_schema': '1'

    no_of_instances: 2 #no of instances you want to attach to the cluster. #optional
    db_instance_class: db.r5.large  #needed when no_of_instances > 0
    instance_parameter_group_values: #needed when no_of_instances > 0
      'performance_schema': '1'
    password_rotation_after_days: 30
```
### Optional Parameters
```
    database_name: ""  # default 'release', "" - None, Update to change DB Name
    enable_cloudwatch_logs_exports: ['audit','error','general','slowquery'] #default #optional
    deletion_protection: True #default #optional
    preferred_backup_window: 00:30-01:30 #default #optional
    preferred_maintenance_window: Sun:02:00-Sun:03:00 #default #optional
    snapshot_identifier: ARN or Name . when snapshot_identifier is defined, master_username,master_user_password is ignored.
```
### Fixed Parameters    
```
    master_username: admin
    master_user_password: Stored in secrets with db_cluster_identifier Name
```

### Author
_Raghu Vamsi_

#### 🔗 Links
[![Linkedin](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/devops-rv/)](https://www.linkedin.com/in/devops-rv/)
[![Medium](https://img.shields.io/badge/-Medium-000000?style=flat&labelColor=000000&logo=Medium&link=https://medium.com/@DevOps-Rv)](https://medium.com/@DevOps-Rv)