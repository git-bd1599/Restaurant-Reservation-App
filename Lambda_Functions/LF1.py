"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve Dining Concierge chatbot which manages restaurant reservations.
Bot, Intent, and Slot models which are compatible with this function can be found in the Lex Console
as part of the 'DiningConcierge' Bot.

"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_slot(intent_request):
    city = intent_request["City"]
    cuisine_type = intent_request["CuisineType"]
    date = intent_request["ReservationDate"]
    reservation_time = intent_request["ReservationTime"]
    numberOfPeople = intent_request["NumberOfPeople"]

    cuisine_types = ['indian', 'chinese', 'thai', 'mexican', 'korean']
    valid_cities = ['new york', 'nyc', 'new york city', 'ny', 'manhattan', 'brooklyn', 'queens', 'staten island']

    if city is not None and city.lower() not in valid_cities:
        return build_validation_result(False,
                                       'City',
                                       'We do not currently support {}, would you like to choose a locality in New York ? '
                                       .format(city))

    if cuisine_type is not None and cuisine_type.lower() not in cuisine_types:
        return build_validation_result(False,
                                       'CuisineType',
                                       'We do not currently support {}, would you like to choose from either Indian, Chinese, Thai, Mexican or  ? '
                                       .format(cuisine_type, cuisine_types))
    
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'ReservationDate', 'I did not understand that, what date would you like to make the reservation?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'ReservationDate', 'You can only reserve a table from today onwards.  What day would you like to make the reservation?')
    

    if reservation_time is not None:
        if len(reservation_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'ReservationTime', None)

        hour, minute = reservation_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'ReservationTime', None)

        if hour < 0 or hour > 24:
            # Outside of business hours
            return build_validation_result(False, 'ReservationTime', 'I am sorry that is not a valid time, please enter a valid time.')

   
    if numberOfPeople is not None and (int(numberOfPeople) < 1):
        #Less than 1 person
        return build_validation_result(False, 'NumberOfPeople', 'The minimum number of people is 1. How many people do you have?')
    #elif math.isnan(numberOfPeople):
        #return build_validation_result(False, 'NumberOfPeople', 'The minimum number of people is 1. How many people do you have?')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def make_reservation(intent_request):
    """
    Performs dialog management and fulfillment for making reservations.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    city = get_slots(intent_request)["City"]
    cuisine_type = get_slots(intent_request)["CuisineType"]
    date = get_slots(intent_request)["ReservationDate"]
    reservation_time = get_slots(intent_request)["ReservationTime"]
    numberOfPeople = get_slots(intent_request)["NumberOfPeople"]
    phone = get_slots(intent_request)["PhoneNumber"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_slot(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        return delegate(intent_request['sessionAttributes'], get_slots(intent_request))
    
    elif source == 'FulfillmentCodeHook':
        sqs = boto3.client('sqs', aws_access_key_id="AKIAZWSA32HVFRCEY5F4", aws_secret_access_key="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")
        response = sqs.get_queue_url(QueueName='DiningChatbot')
        queue_url = response['QueueUrl']
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'Location': {
                'DataType': 'String',
                'StringValue': city
                },
                'Cuisine': {
                'DataType': 'String',
                'StringValue': cuisine_type
                },
                'reservation_date': {
                'DataType': 'String',
                'StringValue': date
                },
                'reservation_time': {
                'DataType': 'String',
                'StringValue': reservation_time
                },
                'numberOfPeople': {
                'DataType': 'Number',
                'StringValue': str(numberOfPeople)
                },
                'PhoneNumber': {
                'DataType': 'String',
                'StringValue': str(phone)
                }
            },
            MessageBody=(
                'Customer details for restaurant reservation'
            )
        )

        print('The message id for the response msg is {}'.format(response['MessageId']))
        
        return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'})

def thank_you(intent_request):
    # Final goodbye message to the end user
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You are welcome'})

def greetings(intent_request):
    #Provide greeting to the user
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hello, how can I help you?'})



""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greetings(intent_request)
    elif intent_name == 'DiningSuggestionIntent':
        return make_reservation(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you(intent_request)


    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
