import boto3
import json
from boto3.dynamodb.conditions import Key
import requests
from requests_aws4auth import AWS4Auth
import random

def lambda_handler(event, context):
    YOUR_ACCESS_KEY = "AKIAZWSA32HVFRCEY5F4"
    YOUR_SECRET_KEY = "qHv7QDK1GrZHiLKjs0PES3ywxGbeOO2Fmcv+bdu2"
    region = "us-west-2"
    service = 'es'

    sqs = boto3.client('sqs', region_name=region,
                        aws_access_key_id= YOUR_ACCESS_KEY, 
                        aws_secret_access_key= YOUR_SECRET_KEY)

    QueueUrl = 'https://sqs.us-west-2.amazonaws.com/666929713642/DiningChatbot'

    message = None

    response = sqs.receive_message(
        QueueUrl=QueueUrl,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    try:
        message = response['Messages'][0]
        city = message['MessageAttributes']['Location']['StringValue']
        cuisine = message['MessageAttributes']['Cuisine']['StringValue']
        phone = message['MessageAttributes']['PhoneNumber']['StringValue']
        numberOfPeople = message['MessageAttributes']['numberOfPeople']['StringValue']
        reservation_date = message['MessageAttributes']['reservation_date']['StringValue']
        reservation_time = message['MessageAttributes']['reservation_time']['StringValue']
        print(city, cuisine, phone, numberOfPeople, reservation_date, reservation_time)

        receipt_handle = message['ReceiptHandle']

        sqs.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)
        
        sms_message = None
        
        awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)
        host = 'https://search-dining-khftlafgbdxmbum7ukajfhcjmq.us-west-2.es.amazonaws.com' # the Amazon ES domain, with https://
        index = 'dining-index'
        url = host + '/' + index + '/_search?q='+str(cuisine)
        
        headers = { "Content-Type": "application/json" }
        r = requests.get(url, auth=awsauth, headers=headers)
        response= r.text
        data = json.loads(response)
        randomSelect = random.randint(0, len(data['hits']['hits'])-3)
        
        def query_data(dynamodb=None):
            if not dynamodb:
                dynamodb = boto3.resource('dynamodb',  aws_access_key_id=YOUR_ACCESS_KEY, aws_secret_access_key=YOUR_SECRET_KEY,region_name = region)

            return(dynamodb.Table('yelp-restaurants'))
        
        restaurant_recommendation = ''
        
        for i in range(3):
            business_id = data['hits']['hits'][randomSelect]['_id']
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
        sms_message = 'Hello, here are my {} restaurant suggestions for {} people on {} at {}:\n'.format(cuisine, numberOfPeople, reservation_date, reservation_time) + restaurant_recommendation + 'Enjoy your meal!' 
        print(sms_message)

        sns = boto3.client("sns", region_name='us-west-2',
                        aws_access_key_id= YOUR_ACCESS_KEY, 
                        aws_secret_access_key= YOUR_SECRET_KEY)

        phoneNumber = '+1'+phone
        

        response = sns.publish(PhoneNumber=phoneNumber, Message=sms_message)
        print(response)

    except KeyError:
        print('Queue is empty')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }




