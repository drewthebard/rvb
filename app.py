# -*- coding: utf-8 -*-
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
modelLoader = ModelLoader("rvb-model.json", "rvb-weights.hdf5")
modelLoader.start()
chars = list('\n !"#$%&\'()*+,-./0123456789:;<>?[]abcdefghijklmnopqrstuvwxyz\x92\xa0¡¿àáäèéêíñóöú')
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
        messages = list(reversed([m.decode('utf-8') for m in cache.lrange(sender, 0, 7)])) if cache.exists(sender) else []
        message = message.lower() if message.endswith(("?","!",".")) else message.lower()+'.' # punctuation
        
        # ignore retransmissions
        if messages and messages[-1] == message:
            return "ok", 200 

        # send loading message
        if modelLoader.is_alive(): 
            send_message(sender, "Grifbot is loading. Please wait.")
            modelLoader.join()

        # generate response
        messages.append(message) 
        dialogue = '\n'.join(
            ['SIMMONS:'+messages[i] if i % 2 == 0 else 'GRIF:'+messages[i] for i in range(len(messages))])
        #print(dialogue)
        response = get_dialogue(dialogue) 

        # send and cache
        cache.lpush(sender, message, response)
        cache.ltrim(sender, 0, 7) # cache last 8 messages
        send_message(sender, response)
    return "ok", 200


def messaging_events(data):
    events = data["entry"][0]["messaging"]
    for event in events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].lower()
        else:
            yield event["sender"]["id"], "i have no idea."


def get_dialogue(message_text, temp=0.5, maxlen=251):
    model = modelLoader.getModel()
    if len(message_text) <= 128:
        starter_lines = modelLoader.getStarterLines()
        starter = "\n".join(starter_lines).lower()
        message_text = starter + '\n' + message_text
    seed_string = message_text + "\nGRIF:"
    startlen = len(seed_string)

    with modelLoader.getGraph().as_default():
        for i in range(maxlen):
            if seed_string.endswith("\n"):
                break
            x = np.array([char_indices.get(c, 1.0) for c in seed_string[-128:]])[np.newaxis,:]
            preds = model.predict(x, verbose=0)[0][-1]
            preds = np.log(preds.clip(min=0.000001)) / temp
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
    # for testing conversations offline
    messages = []
    while True:
        message = input('Say something: ')
        messages.append(message.lower()) 
        dialogue = '\n'.join(
            ['simmons:'+messages[i] if i % 2 == 0 else 'grif:'+messages[i] for i in range(len(messages))])
        print(get_dialogue(dialogue))
    #app.run(debug=True)
