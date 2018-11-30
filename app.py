import json, re, random, requests, redis
import numpy as np
from flask import Flask, request
from textgenrnn import textgenrnn

# load config vars, init app and cache
app = Flask(__name__)
app.config.from_object('config')
cache = redis.from_url(app.config['REDIS_URL'])

# load model
model = textgenrnn(
    weights_path='weights.hdf5',
    vocab_path='vocab.json',
    config_path='config.json',
)
speakers = ['sarge', 'simmons', 'tucker', 'caboose', 'donut']


@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == app.config['VERIFY_TOKEN']:
            return 'Verification token mismatch', 403
        return request.args['hub.challenge']
    return 'Improper verification request'


def preprocess(message, speaker):
    punct = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~\\n\\t\'‘’“”’–—'
    text = speaker + ':' + message.lower() + ('' if message[-1] in '?!.' else '.')
    text = re.sub('([{}])'.format(punct), r' \1 ', text)
    return ' '.join(text.split())


def generate(conversation):
    punct = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~\\n\\t\'‘’“”’–—'
    prefix = ' '.join(conversation) + ' grif : '

    response = model.generate(temperature=1.1, prefix=prefix, return_as_list=True)[0]
    response = response[len(prefix):] + ' '
    conversation.append('grif : ' + response[:-1])
    del conversation[:-1]

    response = re.sub(' ([{}]) '.format(punct), r'\1 ', response)
    response = re.sub("' (t|s|d|m|re|ve|ll)([\s{}])".format(punct), r"'\1\2", response)
    return response.strip() if response.strip() else '...'


@app.route('/', methods=['POST'])
def webhook():
    for sender, message in messaging_events(request.get_json()):
        # get conversation history from cache
        print('Message from {0}: {1}'.format(sender, message))
        try:
            speaker, conversation = json.loads(cache.get(sender))
        except Exception as e:
            speaker, conversation = random.choice(speakers), []
        message = preprocess(message, speaker)
        if conversation and conversation[-1] == message: continue
        conversation.append(message)
        
        # send and cache model response
        response = generate(conversation)
        print('Response to {0}: {1}'.format(sender, response))
        cache.set(sender, json.dumps([speaker, conversation]))
        send_message(sender, response)
    return 'OK'


def messaging_events(data):
    events = data['entry'][0]['messaging']
    for event in events:
        if 'message' in event and 'text' in event['message']:
            yield event['sender']['id'], event['message']['text']


def send_message(recipient, message):
    requests.post(
        'https://graph.facebook.com/v3.1/me/messages',
        params={'access_token': app.config['PAGE_ACCESS_TOKEN']},
        json={
            'recipient': {'id': recipient},
            'message': {'text': message}
        }
    )


if __name__ == '__main__':
    speaker, conversation = random.choice(speakers), []
    while True:
        message = input('Say something: ')
        message = preprocess(message, speaker)
        conversation.append(message)
        response = generate(conversation)
        print(response)
    # app.run(debug=True)
