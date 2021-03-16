import boto3
from boto3.dynamodb.conditions import Key
import json
import requests
from requests_aws4auth import AWS4Auth
import random

region = 'us-west-2' # e.g. us-east-1
service = 'es'
YOUR_ACCESS_KEY = ""
YOUR_SECRET_KEY = ""
#credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)

host = '' # the Amazon ES domain, with https://
index = 'dining-index'
cuisine = 'Indian'
url = host + '/' + index + '/_search?q='+str(cuisine)


# ES 6.x requires an explicit Content-Type header
headers = { "Content-Type": "application/json" }
# Make the signed HTTP request
r = requests.get(url, auth=awsauth, headers=headers)
# Create the response and add some extra content to support CORS
# Add the search results to the response
response= r.text

data = json.loads(response)
randomSelect = random.randint(0, len(data['hits']['hits'])-3)

print(randomSelect)

def query_data(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',  aws_access_key_id=YOUR_ACCESS_KEY, aws_secret_access_key=YOUR_SECRET_KEY,region_name = region)

    return(dynamodb.Table('yelp-restaurants'))


restaurant_recommendation = ''

for i in range(3):
    business_id = data['hits']['hits'][randomSelect]['_id']
    print(business_id)
    table = query_data()
    response = table.query(
        KeyConditionExpression=Key('id').eq(business_id)
    )
    name = response['Items'][0]['name']
    address = response['Items'][0]['location']['display_address']
    ratings = response['Items'][0]['ratings']
    no_of_reviews = response['Items'][0]['reviews']
    message = "{}. {} located at {}, which has {} reviews and a rating of {} on Yelp.\n".format(i+1, name, address, no_of_reviews, ratings)
    restaurant_recommendation = restaurant_recommendation+message
    randomSelect+=1
sms_message = 'Hello, here are my {} restaurant suggestions\n'.format(cuisine) + restaurant_recommendation + 'Enjoy your meal!' 
print(sms_message)
