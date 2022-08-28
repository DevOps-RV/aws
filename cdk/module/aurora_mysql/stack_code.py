import os
import yaml
import boto3
from aws_cdk import (
    Stack,
    aws_rds as rds,
    CfnOutput,
    aws_kms as kms,
    aws_secretsmanager as secretsmanager,
    CfnDynamicReference,
    CfnDynamicReferenceService
)
from constructs import Construct
from commons.logs import setlog

logger = setlog()

account = os.getenv('CDK_DEPLOY_ACCOUNT'),
region = os.getenv('CDK_DEPLOY_REGION')

class AuroraMysqlStack(Stack):
    # defaults
    db_port: int = 3306
    db_engine: str = "aurora-mysql"
    db_name: str = "release"
    enable_cloudwatch_logs_exports: list = [
        'audit', 'error', 'general', 'slowquery']
    deletion_protection: str = "True"
    backup_retention_period: int = 7

    def __init__(self, scope: Construct, construct_id: str,
                 **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # load rds config from repo
        stack_config = self.node.try_get_context("stackDirectory")
        conf_obj = open(f"{os.getcwd()}{stack_config}/config.yml", "r")
        rds_config = yaml.safe_load(conf_obj)
        db_conf = open(f"{os.getcwd()}{stack_config}/db.yml", "r")
        cluster_data = yaml.safe_load(db_conf)


        # stack variables
        self.aws_region = os.environ['CDK_DEPLOY_REGION']
        self.aws_account = os.environ['CDK_DEPLOY_ACCOUNT']

        # get kms key arn using key key alias
        encryption_key = kms.Key.from_lookup(self,
                                             id="kmskey",
                                             alias_name=f"alias/{rds_config['kms_key_alias']}"
                                             )

        logger.info(f"RDS KMS Key: {rds_config['kms_key_alias']}")

        CfnOutput(self, "KmsKeyAlias", value=rds_config['kms_key_alias'])
        CfnOutput(self, "KmsKeyArn", value=encryption_key.key_arn)

        # create db subnet group using above private ec2 subnets
        SubnetGroup = rds.CfnDBSubnetGroup(self,
                                           id=rds_config['db_subnet_group_name'],
                                           db_subnet_group_description=rds_config['db_subnet_group_name'],
                                           subnet_ids=rds_config['existing_subnets'],
                                           db_subnet_group_name=rds_config['db_subnet_group_name'],
                                           )

        logger.info(f"RDS Subnet Group: {SubnetGroup.db_subnet_group_name}")

        CfnOutput(self,
                  id="dbSubnetGroupName",
                  value=SubnetGroup.ref,
                  description="DB Subnet Group Name"
                  )

        # create mysql regional cluster
        for db in cluster_data['mysql_clusters']:

            # cluster admin secret parameters
            ClusterCredentialsParameters = dict(
                id=f"{db['db_cluster_identifier']}-secret",
                description=f"{db['db_cluster_identifier']}-secret",
                generate_secret_string=secretsmanager.CfnSecret.GenerateSecretStringProperty(
                    exclude_characters="\"@/\\ '",
                    exclude_lowercase=False,
                    exclude_numbers=False,
                    exclude_punctuation=False,
                    exclude_uppercase=False,
                    generate_string_key="password",
                    include_space=False,
                    password_length=30,
                    require_each_included_type=False,
                    secret_string_template='{"username":"admin"}'
                ),
                kms_key_id=encryption_key.key_arn,
                name=db['db_cluster_identifier'],
            )

            # create cluster admin secret
            ClusterCredentials = secretsmanager.CfnSecret(
                self, **ClusterCredentialsParameters)

            logger.info(
                f"RDS Aurora-MySql Secrets: {db['db_cluster_identifier']}")

            # create cluster parameter group
            ClusterParameterGroup = rds.CfnDBClusterParameterGroup(self,
                                                                   id=f"{db['db_cluster_identifier']}-ClusterParameterGroup",
                                                                   description=f"{db['db_cluster_identifier']}-ClusterParameterGroup",
                                                                   family=db['family'],
                                                                   parameters=db['cluster_parameter_group_values'],
                                                                   )

            logger.info(
                f"RDS Aurora-MySql Cluster Parameter Group: {ClusterParameterGroup.description}")

            # cluster parameters
            AuroraMysqlClusterParameters = dict(
                id=db['db_cluster_identifier'],
                engine=AuroraMysqlStack.db_engine,
                engine_mode=db['db_engine_mode'],
                port=AuroraMysqlStack.db_port,
                vpc_security_group_ids=rds_config['existing_security_groups'],
                engine_version=db['engine_version'],
                database_name=AuroraMysqlStack.db_name,
                db_cluster_identifier=db['db_cluster_identifier'],
                db_cluster_parameter_group_name=ClusterParameterGroup.ref,
                db_subnet_group_name=SubnetGroup.ref,
                deletion_protection=AuroraMysqlStack.deletion_protection,
                enable_cloudwatch_logs_exports=AuroraMysqlStack.enable_cloudwatch_logs_exports,
                enable_http_endpoint=False,
                enable_iam_database_authentication=True,
                storage_encrypted=True,
                kms_key_id=encryption_key.key_arn,
                master_user_password=CfnDynamicReference(
                    CfnDynamicReferenceService.SECRETS_MANAGER,
                    f"{ClusterCredentials.ref}:SecretString:password"
                ).to_string(),
                master_username=CfnDynamicReference(
                    CfnDynamicReferenceService.SECRETS_MANAGER,
                    f"{ClusterCredentials.ref}:SecretString:username"
                ).to_string(),
                use_latest_restorable_time=False,
                copy_tags_to_snapshot=True,
                backup_retention_period=AuroraMysqlStack.backup_retention_period,
            )

            if 'preferred_backup_window' in db:
                logger.info("preferred_backup_window is defined")
                AuroraMysqlClusterParameters.update(
                    preferred_backup_window=db['preferred_backup_window']),

            if 'preferred_maintenance_window' in db:
                logger.info("preferred_maintenance_window is defined")
                AuroraMysqlClusterParameters.update(
                    preferred_maintenance_window=db['preferred_maintenance_window']
                ),

            if 'snapshot_identifier' in db:
                logger.info(
                    "snapshot_identifier is defined, ignoring master_username value if present")
                AuroraMysqlClusterParameters.update(
                    snapshot_identifier=db['snapshot_identifier']
                ),
                AuroraMysqlClusterParameters.pop('master_username'),
                AuroraMysqlClusterParameters.pop('master_user_password'),

            if 'backup_retention_period' in db and db['backup_retention_period'] > 7:
                logger.info("backup_retention_period defined")
                AuroraMysqlClusterParameters.update(
                    backup_retention_period=db['backup_retention_period']
                ),

            if 'database_name' in db:
                if len(db['database_name']) == 0:
                    logger.info(f"DB Name is not defined")
                    AuroraMysqlClusterParameters.pop('database_name')
                else:
                    logger.info(f"DB Name: {db['database_name']} is defined")
                    AuroraMysqlClusterParameters.update(
                        database_name=db['database_name']
                    ),

            if 'enable_cloudwatch_logs_exports' in db:
                logger.info(
                    f"enable_cloudwatch_logs_exports: {db['enable_cloudwatch_logs_exports']} is defined")
                AuroraMysqlClusterParameters.update(
                    enable_cloudwatch_logs_exports=db['enable_cloudwatch_logs_exports']
                ),

            if 'deletion_protection' in db:
                logger.info(
                    f"deletion_protection updated to: {db['deletion_protection']}")
                AuroraMysqlClusterParameters.update(
                    deletion_protection=db['deletion_protection']
                ),

            AuroraMysqlCluster = rds.CfnDBCluster(
                self, **AuroraMysqlClusterParameters)
            AuroraMysqlCluster.add_depends_on(SubnetGroup)
            AuroraMysqlCluster.add_depends_on(ClusterParameterGroup)

            logger.info(
                f"RDS Aurora-MySql Cluster: {AuroraMysqlCluster.db_cluster_identifier}")

            CfnOutput(self,
                      id=f"{db['db_cluster_identifier']}-endpoint",
                      description=f"{db['db_cluster_identifier']} Cluster Endpoint",
                      value=AuroraMysqlCluster.attr_endpoint_address
                      )

            CfnOutput(self,
                      id=f"{db['db_cluster_identifier']}-AdminPass",
                      description=f"{db['db_cluster_identifier']} Initial Admin Password",
                      value="aws secretsmanager get-secret-value --secret-id " + ClusterCredentials.ref,
                      )

            # attach secret to cluster
            SecretTargetAttachment = secretsmanager.CfnSecretTargetAttachment(self,
                                                                              id=f"{db['db_cluster_identifier']}-SecretAttachment",
                                                                              secret_id=ClusterCredentials.ref,
                                                                              target_id=AuroraMysqlCluster.ref,
                                                                              target_type="AWS::RDS::DBCluster"
                                                                              )
            SecretTargetAttachment.add_depends_on(AuroraMysqlCluster)

            SecretRotationSchedule = secretsmanager.CfnRotationSchedule(self,
                                                                        id=f"{db['db_cluster_identifier']}-SecretRotationSchedule",
                                                                        secret_id=ClusterCredentials.ref,
                                                                        rotate_immediately_on_update=False,
                                                                        rotation_lambda_arn=f"arn:aws:lambda:{region}:{account}:function:{rds_config['secret_rotation_lambda_name']}",
                                                                        rotation_rules=secretsmanager.CfnRotationSchedule.RotationRulesProperty(
                                                                            automatically_after_days=db[
                                                                                'password_rotation_after_days']
                                                                        )
                                                                        )

            SecretRotationSchedule.add_depends_on(SecretTargetAttachment)

            #  add instances to cluster
            if 'no_of_instances' in db and db['no_of_instances'] > 0:

                #  create instance parameter group
                DBParameterGroup = rds.CfnDBParameterGroup(self,
                                                           id=f"{db['db_cluster_identifier']}-InstanceParameterGroup",
                                                           description=f"{db['db_cluster_identifier']}-InstanceParameterGroup",
                                                           family=db['family'],
                                                           parameters=db['instance_parameter_group_values'],
                                                           )
                logger.info(
                    f"RDS Aurora-MySql Instance Parameter Group: {DBParameterGroup.description}")

                # create instances
                for count in range(db['no_of_instances']):
                    instance_number = count + 1

                    AuroraMysqlInstanceParameters = dict(
                        id=f"{db['db_cluster_identifier']}-instance-0{instance_number}",
                        db_cluster_identifier=db['db_cluster_identifier'],
                        db_instance_identifier=f"{db['db_cluster_identifier']}-instance-0{instance_number}",
                        db_instance_class=db['db_instance_class'],
                        db_parameter_group_name=DBParameterGroup.ref,
                        allow_major_version_upgrade=False,
                        auto_minor_version_upgrade=False,
                        engine=AuroraMysqlStack.db_engine,
                        engine_version=db['engine_version'],
                        license_model="general-public-license",
                        monitoring_interval=0,
                        publicly_accessible=False,
                        storage_encrypted=True,
                        use_default_processor_features=False,
                        enable_performance_insights=True,
                        performance_insights_kms_key_id=encryption_key.key_arn,
                        performance_insights_retention_period=7,
                    )

                    AuroraMysqlInstance = rds.CfnDBInstance(
                        self, **AuroraMysqlInstanceParameters)
                    AuroraMysqlInstance.add_depends_on(AuroraMysqlCluster)
                    AuroraMysqlInstance.add_depends_on(DBParameterGroup)

                    logger.info(
                        f"RDS Aurora-MySql Instance {instance_number}: {AuroraMysqlInstance.db_instance_identifier}")

                    CfnOutput(self,
                              id=f"{db['db_cluster_identifier']}-{instance_number}-endpoint",
                              value=AuroraMysqlInstance.attr_endpoint_address,
                              description=f"{db['db_cluster_identifier']}-{instance_number}-endpoint"
                    )
