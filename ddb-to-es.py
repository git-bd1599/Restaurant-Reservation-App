import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2' # e.g. us-east-1
service = 'es'
YOUR_ACCESS_KEY = "AKIAZWSA32HVFRCEY5F4"
YOUR_SECRET_KEY = "qHv7QDK1GrZHiLKjs0PES3ywxGbeOO2Fmcv+bdu2"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)

host = 'https://search-dining-khftlafgbdxmbum7ukajfhcjmq.us-west-2.es.amazonaws.com' # the Amazon ES domain, with https://
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