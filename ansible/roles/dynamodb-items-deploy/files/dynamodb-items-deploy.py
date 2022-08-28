## Author: Raghu Vamsi

import json
import boto3
from botocore.exceptions import ClientError
import logging
import sys

# logging.basicConfig(format='%(levelname)s%(message)s')
logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb')

# Get All DynamoDB Tables
tables_list = [table.name for table in dynamodb.tables.all()]


def get_file_name():
    if len(sys.argv) == 1:
        logger.warning(
            msg=f"\nWARNING : File didn't passed\n"
                f"  USAGE: {sys.argv[0]} file_name.json."
                f"  Exiting ...."
        )
        sys.exit(2)
    else:
        file_name = str(sys.argv[1]).replace(".json", "")
        print(f"Input File Name: {file_name}.json")
    return file_name


def insert_items():
    try:
        file_name = get_file_name()
        with open(f"{file_name}.json") as f:
            table_data = json.load(f)
            for table_name in table_data:

                # Skip if Table doesn't exist
                if table_name not in tables_list:
                    print(f"\n  WARNING : Table - '{table_name}' Doesn't Exist. Skipping ....")

                # Proceed if Given Table exists
                if table_name in tables_list:

                    # set dynamodb table
                    table = dynamodb.Table(f"{table_name}")

                    # logger.info(msg="\n  Table : {table_name}")
                    print(f"\n  Table : {table_name}"
                          # f"   Current No of items: {table.item_count}"
                          # f"\n      Created : {table.creation_date_time}"
                          f"\n      Inserting below items into Table: {table_name}"
                          )

                    for item in table_data.get(table_name):
                        print(f"           item values: {item}")

                        table.wait_until_exists()

                        # insert item into dynamodb table
                        table.put_item(
                            Item=item
                        )

                    # print(f"No of items after insert: {table.item_count}")
                    # ItemCount (integer) --The number of items in the specified table.
                    # DynamoDB updates this value approximately every six hours.
                    # Recent changes might not be reflected in this value.


    except ClientError:
        logger.exception(
            msg=f"\n  ERROR : Couldn't load item data into table: {table_name}"
                f"\n          Please verify the below values"
                f"\n          values: {item} \n "
        )
        raise


if __name__ == '__main__':
    insert_items()
    