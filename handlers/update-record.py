import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('resturant-data-server-dev')  # Adjust to your table name

def convert_floats_to_decimals(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(v) for v in obj]
    return obj

def update(event, context):
    # Attempt to fetch the ID from path parameters
    try:
        record_id = event['pathParameters']['id']
    except KeyError:
        return {
            'statusCode': 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            'body': json.dumps({'error': "Missing 'id' in path parameters"})
        }

    try:
        data = json.loads(event['body'])
        if 'siteData' not in data:
            raise ValueError("Missing 'siteData'")
        site_data = data['siteData']
    except (ValueError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            'body': json.dumps({'error': str(e)})
        }

    # Prepare the update expression and attribute values for siteData replacement
    update_expression = 'SET siteData = :siteData'
    expression_attribute_values = {':siteData': convert_floats_to_decimals(site_data)}

    # Perform the update operation
    try:
        response = table.update_item(
            Key={'id': record_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            'body': json.dumps({'error': "Could not update the record"})
        }

    # Return a success response
    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps({'message': "Successfully updated the record", 'id': record_id, 'updatedAttributes': response.get('Attributes', {})})
    }
