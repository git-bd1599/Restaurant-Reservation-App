import boto3

def scan_data(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',  aws_access_key_id="anything", aws_secret_access_key="anything",region_name = 'us-west-2', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('yelp-restaurants')
    print(table.scan()['Items'])


if __name__ == '__main__':
    scan_data()