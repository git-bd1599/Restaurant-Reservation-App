import boto3
import requests
import json
from requests_aws4auth import AWS4Auth

region = 'us-west-2' # e.g. us-east-1
service = 'es'
YOUR_ACCESS_KEY = ""
YOUR_SECRET_KEY = ""
#credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)

api_key = ''
headers_yelp = {'Authorization' : 'Bearer %s' %api_key}

host = '' # the Amazon ES domain, with https://
index = 'dining-index'
type = 'lambda-type'
url_es = host + '/' + index + '/' + type + '/'

headers = { "Content-Type": "application/json" }

es_dict={}

url = 'https://api.yelp.com/v3/businesses/search'
limit = 50
term = ['Chinese']
for cuisine in term:
    #for offset in range(8):
        params = {
            'term' : cuisine,
            'location' : 'Staten Island',
            'radius' : '10000',
            'limit' : limit,
            #'offset' : offset*50
        }

        req = requests.get(url, params=params, headers=headers_yelp)
        data = json.loads(req.text)
        for i in range(limit):
            id = data['businesses'][i]['id']
            es_dict['name'] = data['businesses'][i]["name"]
            es_dict['id'] = data['businesses'][i]["id"]
            es_dict['cuisine'] = cuisine
            r = requests.put(url_es+id, auth=awsauth, json=es_dict, headers=headers)
        print(r.status_code)
            

