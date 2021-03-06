import boto3
import json

def lambda_handler(event, context):
    YOUR_ACCESS_KEY = "AKIAZWSA32HVFRCEY5F4"
    YOUR_SECRET_KEY = "qHv7QDK1GrZHiLKjs0PES3ywxGbeOO2Fmcv+bdu2"
    region = "us-west-2"

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

        sns = boto3.client("sns", region_name='us-west-2',
                        aws_access_key_id= YOUR_ACCESS_KEY, 
                        aws_secret_access_key= YOUR_SECRET_KEY)

        phoneNumber = '+1'+phone
        sms_message = 'We have received you request for restaurant reservation in {}, for {} cuisine, on {} at {} for {} people. We apologize since our service is currently down we will not be able to service you.'.format(city, cuisine, reservation_date, reservation_time, numberOfPeople)

        response = sns.publish(PhoneNumber=phoneNumber, Message=sms_message)
        print(response)

    except KeyError:
        print('Queue is empty')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }




