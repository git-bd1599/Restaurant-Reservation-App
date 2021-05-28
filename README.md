# Dining Conierge Chatbot

Customer Service is a core service for a lot of businesses around the world and it is
getting disrupted at the moment by Natural Language Processing-powered applications.
In this first assignment we implement a serverless, microservice-driven web
application. Specifically, we will build a Dining Concierge chatbot that sends the user
restaurant suggestions given a set of preferences that the user provides the chatbot with,
through conversation.

### Outline:
We followed the following steps
1. We built and deployed the frontend in an S3 bucket
2. Built an API for the application using API Gateway
    - The API takes input from the frontend and delivers to the backend along with providing response to the frontend once the processing in the backend is done
    - Lambda function (LF0) is created to perform chat functions
3. Built the dining concierge chatbot using Amazon Lex
    - Lambda function (LF1) is created and used as a code hook for Lex, which essentially entails the invocation of the Lambda before Lex responds to any of the requests -- this         gives us chance to manipulate and validate parameters as well as format the bot’s responses.
    - The bot implements three intents
        1. Greeting Intent
        2. Thank you Intent
        3. Dining Suggestion Intent
    - The implementation of an intent entails its setup in Amazon Lex as well as handling its response in the Lambda function code hook.
    - For the Dining Suggestions Intent, the system collects the following pieces of information from the user, through conversation:
        - Location
        - Cuisine
        - Dining Time
        - Number of people
        - Phone number
    - Based on the parameters collected from the user, the system pushes the information collected from the user (location, cuisine, etc.) to an SQS queue (Q1).
        - The system also confirms to the user that it has received their request and that it will notify them over SMS once it has the list of restaurant suggestions.
4. Integrated the Lex chatbot into the chat API
    - When the API receives a request, the system 
        1. extracts the text message from the API request, 
        2. send it to the Lex chatbot 
        3. Waits for the response 
        4. Sends back the response from Lex as the API response.
5. Used the Yelp API to collect 5,000+ random restaurants from Manhattan.
    - 1000 of each of the following five cuisines:
        1. Indian
        2. Chinese
        3. Mexican
        4. Korean
        5. Thai
    - Stored the data collected from Yelp in DynamoDB
6. Created an ElasticSearch instance using the AWS ElasticSearch Service for indexing of the Yelp data.
7. Built a suggestions module, that is decoupled from the Lex chatbot.
    - Created a new Lambda function (LF2) that acts as a queue worker. Whenever it is invoked it 
        - pulls a message from the SQS queue (Q1), 
        - gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB,
        - formats them
        - sends them over text message to the phone number included in the SQS message, using SNS.
    - Set up a CloudWatch event trigger that runs every minute and invokes the Lambda function as a result, this automates the queue worker Lambda to poll and process suggestion       requests on its own.
  
**In summary**, based on a conversation with the customer, the LEX chatbot will identify the customer’s preferred ‘cuisine’. The backend will search through ElasticSearch to get random suggestions of restaurant IDs with this cuisine. At this point, the system would also query the DynamoDB table with these restaurant IDs to find more information about the restaurants to suggest to the customers like name and address of the restaurant. 


![ChatExample](https://user-images.githubusercontent.com/61260957/120046614-2afd0c00-bfd8-11eb-980c-a529d5c5ac95.PNG)
![Architecture](https://user-images.githubusercontent.com/61260957/120046712-63044f00-bfd8-11eb-8345-f1fb3a89f2ba.PNG)

    


