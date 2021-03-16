import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2' # e.g. us-east-1
service = 'es'
YOUR_ACCESS_KEY = ""
YOUR_SECRET_KEY = ""
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)

host = '' # the Amazon ES domain, with https://
index = 'dining-index'
type = 'lambda-type'
url = host + '/' + index + '/' + type + '/'

headers = { "Content-Type": "application/json" }

def handler(event, context):
    count = 0
    for record in event['Records']:
        # Get the primary key for use as the Elasticsearch ID
        id = record['dynamodb']['Keys']['id']['S']

        if record['eventName'] == "INSERT":
            document = record['dynamodb']['NewImage']
            r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
            print(r)
        count += 1
    return str(count) + ' records processed.'
