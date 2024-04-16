import json
import boto3
import uuid
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('resturant-data-server-dev')  # Replace with your DynamoDB table name

def convert_floats_to_decimals(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(v) for v in obj]
    return obj

def create(event, context):
    # Parse the JSON data from the request body
    try:
        data = json.loads(event['body'])
        print(data)
        if 'groupName' not in data['siteData']:
            raise ValueError("Missing 'groupName'")
        if 'siteData' not in data:
            raise ValueError("Missing 'siteData'")
    except ValueError as e:
        return {
            'statusCode': 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            'body': json.dumps({'error': str(e)})
        }

    # Generate a unique ID for this record
    record_id = str(uuid.uuid4())

    # Prepare the item to be inserted
    item = {
        'id': record_id,
        'groupName': data['siteData']['groupName'],
        'siteData': data['siteData'],
        # Add other attributes here
    }
    
    # Optionally, you can merge any additional data passed in the request
    # item.update(data)

    # Insert the item into the DynamoDB table
    try:
        item = convert_floats_to_decimals(item)
        print('item',item)
        table.put_item(Item=item)
    except ClientError as e:
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            'body': json.dumps({'error': "Could not create the record"})
        }

    # Return a success response
    return {
        'statusCode': 200,
        "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        'body': json.dumps({'message': "Successfully created the record", 'id': record_id})
    }
