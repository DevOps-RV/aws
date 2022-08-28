import boto3
import json
import logging
import os
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    """Secrets Manager RDS MySQL Handler

    This handler uses the single-user rotation scheme to rotate an RDS MySQL user credential. This rotation scheme
    logs into the database as the user and rotates the user's own password, immediately invalidating the user's
    previous password.

    The Secret SecretString is expected to be a JSON string with the following format:
    {
        'engine': <required: must be set to 'mysql'>,
        'host': <required: instance host name>,
        'username': <required: username>,
        'password': <required: password>,
        'dbname': <optional: database name>,
        'port': <optional: if not specified, default port 3306 will be used>
    }

    Args:
        event (dict): Lambda dictionary of event parameters. These keys must include the following:
            - SecretId: The secret ARN or identifier
            - ClientRequestToken: The ClientRequestToken of the secret version
            - Step: The rotation step (one of createSecret, setSecret, testSecret, or finishSecret)

        context (LambdaContext): The Lambda runtime information

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        ValueError: If the secret is not properly configured for rotation
        KeyError: If the secret json does not contain the expected keys

    """
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']
    region = os.environ["AWS_REGION"]

    # Setup the client
    service_client = boto3.client(
        'secretsmanager',
        endpoint_url=f"https://secretsmanager.{region}.amazonaws.com"
    )

    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    logger.info(metadata)

    if "RotationEnabled" in metadata and not metadata['RotationEnabled']:
        logger.error(f"Secret {arn} is not enabled for rotation")
        raise ValueError(f"Secret {arn} is not enabled for rotation")

    versions = metadata['VersionIdsToStages']

    if token not in versions:
        logger.error(
            f"Secret version {token} has no stage for rotation of secret {arn}.")
        raise ValueError(
            f"Secret version {token} has no stage for rotation of secret {arn}.")

    if "AWSCURRENT" in versions[token]:
        logger.info(
            f"Secret version {token} already set as AWSCURRENT for secret {arn}.")
        return

    elif "AWSPENDING" not in versions[token]:
        logger.error(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}.")
        raise ValueError(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}.")

    # Call the appropriate step
    if step == "createSecret":
        create_secret(service_client, arn, token)

    elif step == "setSecret":
        set_secret(service_client, arn, token)

    elif step == "testSecret":
        test_secret(service_client, arn, token)

    elif step == "finishSecret":
        finish_secret(service_client, arn, token)

    else:
        logger.error(
            f"lambda_handler: Invalid step parameter: {step} for secret: {arn}")
        raise ValueError(f"Invalid step parameter: {step} for secret: {arn}")


def create_secret(service_client, arn, token):
    """Generate a new secret

    This method first checks for the existence of a secret for the passed in token. If one does not exist, it will generate a
    new secret and put it with the passed in token.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    Raises:
        ValueError: If the current secret is not valid JSON

        KeyError: If the secret json does not contain the expected keys

    """

    # Make sure the current secret exists
    current_dict = get_secret_dict(service_client, arn, "AWSCURRENT")

    # Now try to get the secret version, if that fails, put a new secret
    try:
        get_secret_dict(service_client, arn, "AWSPENDING", token)
        logger.info(f"createSecret: Successfully retrieved secret for {arn}.")

    except service_client.exceptions.ResourceNotFoundException:
        # Get exclude characters from environment variable
        exclude_characters = os.environ['EXCLUDE_CHARACTERS'] if 'EXCLUDE_CHARACTERS' in os.environ else '/@"\'\\'
        # Generate a random password
        passwd = service_client.get_random_password(
            ExcludeCharacters=exclude_characters
        )

        current_dict['password'] = passwd['RandomPassword']

        # Put the secret
        service_client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps(
                current_dict
            ),
            VersionStages=['AWSPENDING']
        )

        logger.info(
            f"createSecret: Successfully put secret for ARN {arn} and version {token}.")


def set_secret(service_client, arn, token):
    """Set the pending secret in the database

    This method tries to login to the database with the AWSPENDING secret and returns on success. If that fails, it
    tries to login with the AWSCURRENT and AWSPREVIOUS secrets. If either one succeeds, it sets the AWSPENDING password
    as the user password in the database. Else, it throws a ValueError.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist

        ValueError: If the secret is not valid JSON or valid credentials are found to login to the database

        KeyError: If the secret json does not contain the expected keys

    """
    try:
        previous_dict = get_secret_dict(service_client, arn, "AWSPREVIOUS")

    except (service_client.exceptions.ResourceNotFoundException, KeyError):
        previous_dict = None

    current_dict = get_secret_dict(service_client, arn, "AWSCURRENT")

    pending_dict = get_secret_dict(service_client, arn, "AWSPENDING", token)

    # First try to login with the pending secret, if it succeeds, return
    conn = get_connection(pending_dict)
    # if conn is not None:
    if conn:
        conn.close()
        logger.info(
            f"setSecret: AWSPENDING secret is already set as password in MySQL DB for secret {arn}.")
        return

    # Make sure the user from current and pending match
    if current_dict['username'] != pending_dict['username']:
        logger.error(
            f"setSecret: Attempting to modify user {pending_dict['username']} other than current user {current_dict['username']}")
        raise ValueError(
            f"Attempting to modify user {pending_dict['username']} other than current user {current_dict['username']}")

    # Make sure the host from current and pending match
    if current_dict['host'] != pending_dict['host']:
        logger.error(
            f"setSecret: Attempting to modify user for host {pending_dict['host']} other than current host {current_dict['host']}")
        raise ValueError(
            f"Attempting to modify user for host {pending_dict['host']} other than current host {current_dict['host']}")

    # Now try the current password
    conn = get_connection(current_dict)

    # If both current and pending do not work, try previous
    if not conn and previous_dict:
        # Update previous_dict to leverage current SSL settings
        previous_dict.pop('ssl', None)
        if 'ssl' in current_dict:
            previous_dict['ssl'] = current_dict['ssl']

        conn = get_connection(previous_dict)

        # Make sure the user/host from previous and pending match
        if previous_dict['username'] != pending_dict['username']:
            logger.error(
                f"setSecret: Attempting to modify user: {pending_dict['username']} other than previous valid user: {previous_dict['username']}")
            raise ValueError(
                f"Attempting to modify user: {pending_dict['username']} other than previous valid user: {previous_dict['username']}")

        if previous_dict['host'] != pending_dict['host']:
            logger.error(
                f"setSecret: Attempting to modify user for host: {pending_dict['host']} other than previous host: {previous_dict['host']}")
            raise ValueError(
                f"Attempting to modify user for host: {pending_dict['host']} other than previous host: {previous_dict['host']}")

    # If we still don't have a connection, raise a ValueError
    if not conn:
        logger.error(
            f"setSecret: Unable to log into database with previous, current, or pending secret of secret ARN: {arn}")
        raise ValueError(
            f"Unable to log into database with previous, current, or pending secret of secret ARN: {arn}")

    # Now set the password to the pending password
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            ver = cur.fetchone()
            password_option = get_password_option(ver[0])
            cur.execute("SET PASSWORD = " + password_option,
                        pending_dict['password'])
            conn.commit()

            logger.info(
                f"setSecret: Successfully set password for user: {pending_dict['username']} in MySQL DB for secret ARN: {arn}.")

    finally:
        conn.close()


def test_secret(service_client, arn, token):
    """Test the pending secret against the database

    This method tries to log into the database with the secrets staged with AWSPENDING and runs
    a permissions check to ensure the user has the corrrect permissions.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist

        ValueError: If the secret is not valid JSON or valid credentials are found to login to the database

        KeyError: If the secret json does not contain the expected keys

    """
    # Try to login with the pending secret, if it succeeds, return
    conn = get_connection(get_secret_dict(
        service_client, arn, "AWSPENDING", token))
    if conn:
        # This is where the lambda will validate the user's permissions. Uncomment/modify the below lines to
        # tailor these validations to your needs
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW()")
                conn.commit()
        finally:
            conn.close()

        logger.info(
            f"testSecret: Successfully signed into MySQL DB with AWSPENDING secret in {arn}.")
        return

    else:
        logger.error(
            f"testSecret: Unable to log into database with pending secret of secret ARN: {arn}.")
        raise ValueError(
            f"Unable to log into database with pending secret of secret ARN: {arn}.")


def finish_secret(service_client, arn, token):
    """Finish the rotation by marking the pending secret as current

    This method finishes the secret rotation by staging the secret staged AWSPENDING with the AWSCURRENT stage.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    """
    # First describe the secret to get the current version
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None

    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                logger.info(
                    f"finishSecret: Version {version} already marked as AWSCURRENT for {arn}")
                return

            current_version = version
            break

    # Finalize by staging the secret version current
    service_client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version
    )

    logger.info(
        f"finishSecret: Successfully set AWSCURRENT stage to version {token} for secret {arn}.")


def get_connection(secret_dict):
    """Gets a connection to MySQL DB from a secret dictionary

    This helper function uses connectivity information from the secret dictionary to initiate
    connection attempt(s) to the database. Will attempt a fallback, non-SSL connection when
    initial connection fails using SSL and fall_back is True.

    Args:
        secret_dict (dict): The Secret Dictionary

    Returns:
        Connection: The pymysql.connections.Connection object if successful. None otherwise

    Raises:
        KeyError: If the secret json does not contain the expected keys

    """
    # Parse and validate the secret JSON string
    port = int(secret_dict['port']) if 'port' in secret_dict else 3306
    dbname = secret_dict['dbname'] if 'dbname' in secret_dict else None

    # Get SSL connectivity configuration
    use_ssl, fall_back = get_ssl_config(secret_dict)

    # if an 'ssl' key is not found or does not contain a valid value, attempt an SSL connection and fall back to non-SSL on failure
    conn = connect_and_authenticate(secret_dict, port, dbname, use_ssl)
    if conn or not fall_back:
        return conn
    else:
        return connect_and_authenticate(secret_dict, port, dbname, False)


def get_ssl_config(secret_dict):
    """Gets the desired SSL and fall back behavior using a secret dictionary

    This helper function uses the existance and value the 'ssl' key in a secret dictionary
    to determine desired SSL connectivity configuration. Its behavior is as follows:
        - 'ssl' key DNE or invalid type/value: return True, True
        - 'ssl' key is bool: return secret_dict['ssl'], False
        - 'ssl' key equals "true" ignoring case: return True, False
        - 'ssl' key equals "false" ignoring case: return False, False

    Args:
        secret_dict (dict): The Secret Dictionary

    Returns:
        Tuple(use_ssl, fall_back): SSL configuration
            - use_ssl (bool): Flag indicating if an SSL connection should be attempted
            - fall_back (bool): Flag indicating if non-SSL connection should be attempted if SSL connection fails

    """
    # Default to True for SSL and fall_back mode if 'ssl' key DNE
    if 'ssl' not in secret_dict:
        return True, True

    # Handle type bool
    if isinstance(secret_dict['ssl'], bool):
        return secret_dict['ssl'], False

    # Handle type string
    if isinstance(secret_dict['ssl'], str):
        ssl = secret_dict['ssl'].lower()
        if ssl == "true":
            return True, False
        elif ssl == "false":
            return False, False
        else:
            # Invalid string value, default to True for both SSL and fall_back mode
            return True, True

    # Invalid type, default to True for both SSL and fall_back mode
    return True, True


def connect_and_authenticate(secret_dict, port, dbname, use_ssl):
    """Attempt to connect and authenticate to a MySQL instance

    This helper function tries to connect to the database using connectivity info passed in.
    If successful, it returns the connection, else None

    Args:
        - secret_dict (dict): The Secret Dictionary
        - port (int): The databse port to connect to
        - dbname (str): Name of the database
        - use_ssl (bool): Flag indicating whether connection should use SSL/TLS

    Returns:
        Connection: The pymongo.database.Database object if successful. None otherwise

    Raises:
        KeyError: If the secret json does not contain the expected keys

    """
    ssl = {'ca': '/etc/pki/tls/cert.pem', } if use_ssl else None

    # Try to obtain a connection to the db
    try:
        # Checks hostname and verifies server certificate implictly when 'ca' key is in 'ssl' dictionary
        conn = pymysql.connect(
            host=secret_dict['host'],
            user=secret_dict['username'],
            password=secret_dict['password'],
            port=port,
            database=dbname,
            connect_timeout=5,
            ssl=ssl
        )

        logger.info("Successfully established %s connection as user '%s' with host: '%s'" % (
            "SSL/TLS" if use_ssl else "non SSL/TLS", secret_dict['username'], secret_dict['host']))
        return conn

    except pymysql.OperationalError as e:
        if 'certificate verify failed: IP address mismatch' in e.args[1]:
            logger.error(
                f"Hostname verification failed when estlablishing SSL/TLS Handshake with host: {secret_dict['host']}")
        return None


def get_secret_dict(service_client, arn, stage, token=None):
    """Gets the secret dictionary corresponding for the secret arn, stage, and token

    This helper function gets credentials for the arn and stage passed in and returns the dictionary by parsing the JSON string

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version, or None if no validation is desired

        stage (string): The stage identifying the secret version

    Returns:
        SecretDictionary: Secret dictionary

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist

        ValueError: If the secret is not valid JSON

    """
    required_fields = ['host', 'username', 'password']

    # Only do VersionId validation against the stage if a token is passed in
    if token:
        secret = service_client.get_secret_value(
            SecretId=arn,
            VersionId=token,
            VersionStage=stage
        )
    else:
        secret = service_client.get_secret_value(
            SecretId=arn,
            VersionStage=stage
        )
    plaintext = secret['SecretString']
    secret_dict = json.loads(plaintext)

    # Run validations against the secret
    if 'engine' not in secret_dict or secret_dict['engine'] != 'mysql':
        raise KeyError(
            "Database engine must be set to 'mysql' in order to use this rotation lambda")

    for field in required_fields:
        if field not in secret_dict:
            raise KeyError(f"{field} key is missing from secret JSON")

    # Parse and return the secret JSON string
    return secret_dict


def get_password_option(version):
    """Gets the password option template string to use for the SET PASSWORD sql query

    This helper function takes in the mysql version and returns the appropriate password option template string that can
    be used in the SET PASSWORD query for that mysql version.

    Args:
        version (string): The mysql database version

    Returns:
        PasswordOption: The password option string

    """
    if version.startswith("8"):
        return "%s"
    else:
        return "PASSWORD(%s)"
