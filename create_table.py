import boto3


def create_yelp_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',  aws_access_key_id="anything", aws_secret_access_key="anything",region_name = 'us-west-2', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='yelp-restaurants',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


if __name__ == '__main__':
    yelp_table = create_yelp_table()
    print("Table status:", yelp_table.table_status)