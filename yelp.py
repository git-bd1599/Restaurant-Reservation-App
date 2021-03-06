import requests
import json
import time
from time import strptime
import boto3
from decimal import Decimal

api_key = '1r3sM0guSg71-4KcUg_zKbz-MYpLfW-jsuPBT1ZUKyyjOjFVkffO5QJJMXLxAAqiK8rYN6kZte26ZQmB9roAjtjJKBDpUopsIVK_P3IYos1kSCnYOitFkD3x_pYuYHYx'
headers = {'Authorization' : 'Bearer %s' %api_key}


#dataFile = open('yelp.json', 'w')
yelp_dict = {}

YOUR_ACCESS_KEY = "AKIAZWSA32HVFRCEY5F4"
YOUR_SECRET_KEY = "qHv7QDK1GrZHiLKjs0PES3ywxGbeOO2Fmcv+bdu2"
region = "us-west-2"

def put_data(restaurants, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',  aws_access_key_id = YOUR_ACCESS_KEY, aws_secret_access_key = YOUR_SECRET_KEY, region_name = region)
    table = dynamodb.Table('yelp-restaurants')
    table.put_item(Item=restaurants)

url = 'https://api.yelp.com/v3/businesses/search'
term = ['Indian'] #, 'Chinese', 'Thai', 'Mexican', 'Korean']
for cuisine in term:
    #for offset in range(20):
        params = {
            'term' : cuisine,
            'location' : 'Manhattan',
            'radius' : '10000',
            'limit' : '1',
            #'offset' : offset*50
        }

        req = requests.get(url, params=params, headers=headers)
        data = json.loads(req.text)
        #json.dump(data['businesses'], dataFile)
        #dataFile.write(',')
        for placeholder in data['businesses']:
            yelp_dict['id'] = placeholder['id']
            yelp_dict['name'] = placeholder['name']
            yelp_dict['reviews'] = Decimal(placeholder['review_count'])
            yelp_dict['ratings'] = Decimal(placeholder['rating'])
            coordinate_values = placeholder['coordinates'].items()
            yelp_dict['coordinates'] = {key: str(value) for key, value in coordinate_values}
            yelp_dict['location'] = placeholder['location']
            yelp_dict['insertedAtTimestamp'] = time.gmtime()
            put_data(yelp_dict)
        print(req.status_code)
    


    