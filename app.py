import os, sys, json, random, requests, redis
from dotenv import load_dotenv
from flask import Flask, request

import numpy as np
from utils import ModelLoader

# load config vars, init app and cache
load_dotenv(".env")
app = Flask(__name__)
cache = redis.from_url(os.environ.get("REDIS_URL"))

# load keras model
modelLoader = ModelLoader("model.json", "weights.hdf5")
modelLoader.start()
chars = ['\n', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '>', '?', '[', ']', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '\x92', '\xa0', '¡', '¿', 'à', 'á', 'ä', 'è', 'é', 'ê', 'í', 'ñ', 'ó', 'ö', 'ú']
char_indices = dict((c, i) for i, c in enumerate(chars))


@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Improper verification request", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    for sender, message in messaging_events(data):
        #print("Incoming from {sender}: {text}".format(sender=sender, message=message))
        # get message history from cache
        messages = [m.decode('utf-8') for m in cache.lrange(sender, 0, 7)] if cache.exists(sender) else []
        messages.append(message)
        dialogue = '\n'.join(
            ['simmons:'+messages[i] if i % 2 == 0 else 'grif:'+messages[i] for i in range(len(messages))])
        print(dialogue)

        response = get_dialogue(dialogue) 
        cache.lpush(sender, message, response)
        cache.ltrim(sender, 0, 7) # cache last 8 messages
        send_message(sender, response)
    return "ok"


def messaging_events(data):
    events = data["entry"][0]["messaging"]
    for event in events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].lower()
        else:
            yield event["sender"]["id"], "i have no idea."


def get_dialogue(message_text, temp=0.65, maxlen=250):
    model = modelLoader.getModel()
    if model is None:
        return "grifbot is loading"

    starter_lines = modelLoader.getStarterLines()
    random.shuffle(starter_lines)
    starter = "\n".join(starter_lines)
    seed_string = starter + message_text + "\n grif:"
    startlen = len(seed_string)

    with modelLoader.getGraph().as_default():
        for i in range(maxlen):
            if seed_string.endswith("\n"):
                break
            x = np.array([char_indices.get(c, 1.0) for c in seed_string[-64:]])[np.newaxis,:]
            preds = model.predict(x, verbose=0)[0][-1]
            preds = np.log(preds) / temp
            exp_preds = np.exp(preds)
            preds = exp_preds / np.sum(exp_preds)
            next_char = np.random.choice(chars, p=preds)
            seed_string = seed_string + next_char
    
    return seed_string[startlen:-1]


def send_message(recipient, message):
    #print("Sending to {recipient}: {message}".format(recipient=recipient, message=message)) # for testing only
    params = { "access_token": os.environ["PAGE_ACCESS_TOKEN"] }
    headers = { "Content-Type": "application/json" }
    data = json.dumps({
        "recipient": {
            "id": recipient
        },
        "message": {
            "text": message
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.text)


if __name__ == '__main__':
    #while True: # for testing conversations offline
    #    ins = input('Say something: ')
    #    print(get_dialogue(ins))
    app.run(debug=True)
