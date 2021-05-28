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
    -Lambda function (LF1) is created and used as a code hook for Lex, which essentially entails the invocation of the Lambda before Lex responds to any of the requests -- this gives us chance to manipulate and validate parameters as well as format the bot’s responses.

