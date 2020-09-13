from __future__ import print_function

import re

import json
import os

from flask import Flask
from flask import request
from flask import make_response

from textblob import TextBlob

import requests

from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.config['INTEGRATIONS'] = ['ACTIONS_ON_GOOGLE']


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)

    r.headers['Content-Type'] = 'application/json'

    return r

def processRequest(req):

    if req.get("queryResult").get("action") == "weight":
        result = req.get("queryResult")
        parameters = result.get("parameters")
        weight = parameters["number"]

        if weight <= 35:
            size = make_size(weight)
            data = requests.post('http://35.154.227.98/api/example/sizeWiseProducts', data={'size': size}, auth=HTTPBasicAuth('mamypokopants@gmail.com', 'Neuro@123'))
            res = makeWebhookResult(0, data)
        else:
            res = speech_output("Please enter a weight less than 35 kg ")

    if req.get("queryResult").get("action") == "more":
        result = req.get("queryResult")
        parameters = result.get("parameters")
        weight = parameters["weight"]

        size = make_size(weight)
        data = requests.post('http://35.154.227.98/api/example/sizeWiseProducts', data={'size': size},
                             auth=HTTPBasicAuth('mamypokopants@gmail.com', 'Neuro@123'))
        res = makeWebhookResult(10, data)

    elif req.get("queryResult").get("action") == "wipes":
        res = webhook_wipes()

    elif req.get("queryResult").get("action") == "email":
        result = req.get("queryResult")
        parameters = result.get("parameters")
        email = parameters['email']
        name = parameters['name']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            res = speech_output("This is not correct, please enter the correct e-mail again. ")
        else:
            with open("down_names.csv", "a") as file1:
                file1.write(name)
                file1.write(',')
                file1.write(email)
                file1.write('\n')
            res = {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "Thanks, I can help you with the following: "
                                    }
                                }
                            ],
                            "suggestions": [
                                {
                                    "title": "Products"
                                },
                                {
                                    "title": "Feedback"
                                },
                                {
                                    "title": "Customer Care"
                                },
                                {
                                    "title": "App Download"
                                }
                            ]
                        }
                    }
                }
            }

    elif req.get("queryResult").get("action") == "feedback1":
        result = req.get("queryResult")
        parameters = result.get("parameters")
        feedback = parameters['any']
        blob = TextBlob(feedback)

        rating = blob.polarity

        if rating > 0.05:
            res = rating_result("Thanks! We're glad to see that you are happy with our services ")
        else:
            res = rating_result("Sorry for the inconvenience caused, we will get in touch ")

    return res


def makeWebhookResult(a, data):

    new = json.loads(data.text)

    list = []

    for i in range(a, len(new["data"])):

        blob = TextBlob(new["data"][i]["product_sub_title"])
        newnum = blob.words
        newnum1 = newnum[1]
        new1 = {
            "title": "Buy Pack of "+newnum1+" Diapers",
            "openUrlAction": {
                "url": new["data"][i]["final_url"]
            },
            "description": "Mamy Poko Pants",
            "image": {
                "url": new["data"][i]["pro_image"],
                "accessibilityText": "Image alternate text"
            }
        }
        list.append(new1)
        if i == 9:
            break

    if len(new["data"]) == 1:
        return {
            "fulfillmentText": "This is a text response",
            "fulfillmentMessages": [
                {
                    "card": {
                        "title": "card title",
                        "imageUri": new["data"][0]["pro_image"],
                        "buttons": [
                            {
                                "text": "Click here to buy",
                                "postback": "https://assistant.google.com/"
                            }
                        ]
                    }
                }
            ],
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": "Here are your diapers "
                                }
                            },
                            {
                                "basicCard": {
                                    "title": "Mamy Poko Pants",
                                    "image": {
                                        "url": new["data"][0]["pro_image"],
                                        "accessibilityText": "Image alternate text"
                                    },
                                    "buttons": [
                                        {
                                            "title": "Click here to buy",
                                            "openUrlAction": {
                                                "url": new["data"][0]["final_url"]
                                            }
                                        }
                                    ],
                                    "imageDisplayOptions": "CROPPED"
                                }
                            },
                            {
                                "simpleResponse": {
                                    "textToSpeech": "May I help you with something else? "
                                }
                            },

                        ],
                        "suggestions": [
                            {
                                "title": "Yes"
                            },
                            {
                                "title": "No"
                            }

                        ]
                    }
                }
            }
        }

    else:
        if a==0 and len(new["data"]) > 10:
            return {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "Here are your diapers "
                                    }
                                },
                                {
                                    "carouselBrowse": {
                                        "items": list
                                    }
                                },
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "May I help you with something else?"
                                    }
                                }

                            ],
                            "suggestions": [
                                {
                                    "title": "More items"
                                },
                                {
                                    "title": "Yes"
                                },
                                {
                                    "title": "No"
                                }

                            ]
                        }
                    }
                }
            }

        else:
            return {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "Here are your diapers "
                                    }
                                },
                                {
                                    "carouselBrowse": {
                                        "items": list
                                    }
                                },
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "May I help you with something else?"
                                    }
                                }

                            ],
                            "suggestions": [
                                {
                                    "title": "Yes"
                                },
                                {
                                    "title": "No"
                                }

                            ]
                        }
                    }
                }
            }


def webhook_wipes():

    return {
        "fulfillmentText": "This is a text response",
        "fulfillmentMessages": [
            {
                "card": {
                    "title": "card title",
                    "subtitle": "card text",
                    "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
                    "buttons": [
                        {
                            "text": "button text",
                            "postback": "https://assistant.google.com/"
                        }
                    ]
                }
            }
        ],
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": "Here are your diapers "
                            }
                        },
                        {
                            "basicCard": {
                                "title": "Title: this is a title",
                                "subtitle": "This is a subtitle",
                                "formattedText": "This is a basic card.  Text in a basic card can include ",
                                "image": {
                                    "url": "https://example.com/image.png",
                                    "accessibilityText": "Image alternate text"
                                },
                                "buttons": [
                                    {
                                        "title": "This is a button",
                                        "openUrlAction": {
                                            "url": "https://assistant.google.com/"
                                        }
                                    }
                                ],
                                "imageDisplayOptions": "CROPPED"
                            }
                        },
                        {
                            "simpleResponse": {
                                "textToSpeech": "May I help you with something else? "
                            }
                        },

                    ],
                    "suggestions": [
                        {
                            "title": "Yes"
                        },
                        {
                            "title": "No"
                        }

                    ]
                }
            }
        }
    }


def rating_result(speech):
    return {
        "fulfillmentText": speech,
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": speech
                            }
                        },
                        {
                            "simpleResponse": {
                                "textToSpeech": "May I help you with something else?"
                            }
                        }
                    ],
                    "suggestions": [
                        {
                            "title": "Yes"
                        },
                        {
                            "title": "No"
                        }

                    ]
                }
            }
        }
    }


def speech_output(speech):
    return {
        "fulfillmentText": speech,
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": speech
                            }
                        }
                    ]

                }
            }
        }
    }


def make_size(weight):
    if weight > 0 and weight <= 3:
        size = 'NB-0'
    elif weight > 3 and weight <= 5:
        size = 'NB-1'
    elif weight > 5 and weight <= 8:
        size = 'S'
    elif weight > 8 and weight <= 12:
        size = 'M'
    elif weight > 12 and weight <= 14:
        size = 'L'
    elif weight > 14 and weight <= 17:
        size = 'XL'
    elif weight > 17 and weight <= 25:
        size = 'XXL'
    elif weight > 25 and weight <= 35:
        size = 'XXXL'

    return size


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5060))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
