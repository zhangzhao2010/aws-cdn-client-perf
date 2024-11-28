import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table_name = 'cdn-perf-reports'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        uuid = event['pathParameters']['uuid']
        body = event['body']

        table.put_item(
            Item={
                'uuid': uuid,
                'source_ip': event['requestContext']['http']['sourceIp'],
                'x-forwarded-for': event['headers']['x-forwarded-for'],
                'data': body,
                'timestamp': int(time.time())
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'strict-origin-when-cross-origin': 'strict-origin-when-cross-origin'
            },
            'body': json.dumps({'message': 'Report saved successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
