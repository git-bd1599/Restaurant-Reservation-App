import boto3
import json
from decimal import Decimal

yelp_dict = {}
def put_data(restaurants, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',  aws_access_key_id="anything", aws_secret_access_key="anything",region_name = 'us-west-2', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('yelp-restaurants')
    table.put_item(Item=restaurants)

if __name__ == '__main__':
    with open('yelp.json') as json_file:
        restaurant_list = json.load(json_file, parse_float=Decimal, strict=False)
    for placeholder in restaurant_list['businesses']:
        yelp_dict['id'] = placeholder['id']
        yelp_dict['name'] = placeholder['name']
        yelp_dict['reviews'] = placeholder['review_count']
        yelp_dict['ratings'] = placeholder['rating']
        yelp_dict['coordinates'] = placeholder['coordinates']
        yelp_dict['location'] = placeholder['location']
        put_data(yelp_dict)