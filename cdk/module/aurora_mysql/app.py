#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aurora_mysql import AuroraMysqlStack

app = cdk.App()
stack_name = app.node.try_get_context("stackName")

AuroraMysqlStack = AuroraMysqlStack(
    app,
    stack_name,

    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    env=cdk.Environment(
        account=os.getenv('CDK_DEPLOY_ACCOUNT'),
        region=os.getenv('CDK_DEPLOY_REGION')
    ),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */


    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )
AuroraMysqlStack.add_transform("AWS::SecretsManager-2020-07-23")
#AuroraMysqlStack.template_options.transforms = ["AWS::SecretsManager-2020-07-23"]
app.synth()
