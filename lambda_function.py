import json
import boto3
import os
import time

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        # 获取路径参数中的uuid
        uuid = event['pathParameters']['uuid']

        # 获取请求体中的JSON数据
        body = event['body']

        # 将数据存储在DynamoDB中
        table.put_item(
            Item={
                'uuid': uuid,
                'data': body,
                'source_ip': event['requestContext']['http']['sourceIp'],
                'x-forwarded-for': event['headers']['x-forwarded-for'],
                'headers': json.dumps(event['headers']),
                'http': json.dumps(event['requestContext']['http']),
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
