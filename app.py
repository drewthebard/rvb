import os, sys, json
import requests
import numpy as np
from dotenv import load_dotenv
from keras.models import Sequential, model_from_json
from flask import Flask, request

app = Flask(__name__)
load_dotenv(".env")

#with open("model.json", "r") as f:
#    model_json = f.read()
#model = model_from_json(model_json)
#model.load_weights("weights.hdf5")
#chars = []
#char_indices = dict((c, i) for i, c in enumerate(chars))

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "I would just like to let everyone know that I suck.", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    print(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"] # the facebook ID of the person sending you the message
                    message_text = messaging_event["message"]["text"]  # the message's text
                    send_message(sender_id, get_dialogue(message_text))
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def get_dialogue(message_text, temp=0.7, maxlen=50):
    return "Hi, it works then."
    seed_string = message_text + "\n grif:"
    startlen = len(seed_string)
    for i in range(maxlen):
        if seed_string.endswith("\n"):
            break
        x = np.array([char_indices[c] for c in seed_string[-40:]])[np.newaxis,:]
        preds = model.predict(x, verbose=0)[0][-1]
        preds = np.log(preds) / temp
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        next_char = choice(chars, p=preds)
        seed_string = seed_string + next_char
    
    return seed_string[startlen:-1]

def send_message(recipient_id, message_text):

    print("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = { "access_token": os.environ["PAGE_ACCESS_TOKEN"] }
    headers = { "Content-Type": "application/json" }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

if __name__ == '__main__':
    app.run(debug=True)
