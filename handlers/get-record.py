# get_handler.py
import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from json import JSONEncoder

class DecimalEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # or float(obj) if you need it as a float
        return super(DecimalEncoder, self).default(obj)

# Initialize a DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("resturant-data-server-dev")

def get(event, context):
    # Extract the "id" from the path parameters
    record_id = event["pathParameters"]["id"]
    print(record_id)
    try:
        # Attempt to retrieve the item from DynamoDB
        response = table.get_item(Key={"id": record_id})
    except ClientError as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": "Could not fetch the record"})
        }
    
    # If the item could not be found
    if "Item" not in response:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": "Item not found"})
        }

    # Return the retrieved item
    body = json.dumps(response["Item"], cls=DecimalEncoder)
    return {
        "statusCode": 200,
        "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        "body": body
    }
