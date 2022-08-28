
# Amazon RDS Aurora-MySQL single user

RDS Aurora-MySQL Doesn't support Hosted Rotation Lambda.

Here is the template to create lambda function to rotate Aurora-MySQL single user

```
Template name: SecretsManagerRDSAuroraMySQLRotationSingleUser
```
Supported database/service: Aurora-MySQL database hosted on an Amazon Relational Database Service (Amazon RDS) database instance.
Rotation strategy: Single user rotation strategy.
## Requirement

Expected SecretString structure:
Amazon RDS Aurora-MySQL secret structure.

    The Secret SecretString is expected to be a JSON string with the following format

```json

    {
        'engine': <required: must be set to 'mysql'>,
        'host': <required: instance host name>,
        'username': <required: username>,
        'password': <required: password>,
        'dbname': <optional: database name>,
        'port': <optional: if not specified, default port 3306 will be used>
    }

```
    
## Deployment


* Install the required packages - PyMySQL

```bash
python3 -m pip install -r requirements.txt -t .
```
* Make the zip lambda_function.py and packages (pymysql, PyMySQL-XXX.dist-info) together
* Create the lambda funtion uploading the zip file
* configure the vpc and security groups and set up Permissions for rotation.
* Add rotation to the existing secret credentails
* Choose the above created lambda function
* Make sure the rotation function can access both the secret and the database or other service. See Network access for the rotation function.
* Try rotate secret immediately and verify

### Author: Raghu Vamsi

#### 🔗 Links
[![Linkedin](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/devops-rv/)](https://www.linkedin.com/in/devops-rv/)
[![Medium](https://img.shields.io/badge/-Medium-000000?style=flat&labelColor=000000&logo=Medium&link=https://medium.com/@DevOps-Rv)](https://medium.com/@DevOps-Rv)