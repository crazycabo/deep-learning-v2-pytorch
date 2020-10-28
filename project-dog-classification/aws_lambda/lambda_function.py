import os
import io
import boto3
import json
import csv
import base64
import numpy as np

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    try:
        data = json.loads(json.dumps(event))
        payload = data['body']

        encoded = base64.decodebytes(payload.encode('utf-8'))
        img = bytearray(encoded)
    except:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': 'Incompabile image type',
                'message': 'Try again with a different image'
            })
        }

    try:
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/octet-stream',
            Body=img
            )

        result = json.loads(response['Body'].read().decode())
        breed_index = int(np.argmax(result))
        breed_name = get_breed(breed_index)
    except:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': 'Exception thrown from Sagemaker endpoint',
                'message': 'See Cloudwatch logs for details. Try an image with 3 tensors or RGB channels only.'
            })
        }

    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({
            'breed_name': breed_name.strip('\n'),
            'breed_index': breed_index
        })
    }

def get_breed(index):
    breeds_list = []

    with open("breeds_dog.txt", "r") as dog_breeds:
        breeds_list = dog_breeds.readlines()

    return breeds_list[index]
