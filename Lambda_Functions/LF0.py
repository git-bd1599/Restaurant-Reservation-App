import json
import boto3

def lambda_handler(event, context):

    client = boto3.client('lex-runtime')
    
    response = client.post_text(
        botName='DiningConciergeBot',
        botAlias='dcbot',
        userId= 'bot',
        sessionAttributes={
            },
        requestAttributes={
        },
        inputText = event['messages'][0]['unstructured']['text']
    )
    print("Message from bot:" +response["message"])
    return {
        'statusCode': 200,
        'messages': [{
                "type": "unstructured",
                "unstructured": {
                    "text": response["message"]
                                }
                      }]
    }
