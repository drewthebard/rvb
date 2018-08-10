import os, sys, json, random, requests, redis, keras, tensorflow
import numpy as np
from flask import Flask, request

# load config vars, init app and cache
app = Flask(__name__)
app.config.from_object('config')
cache = redis.from_url(app.config['REDIS_URL'])

# load pytorch model
with open('rvb-model.json') as f:
    model = keras.models.model_from_json(f.read())
model.load_weights('rvb-weights.hdf5')
graph = tensorflow.get_default_graph()
chars = list('\n !"#$%&\'()*+,-./0123456789:;<>?_`abcdefghijklmnopqrstuvwxyz{}~¡¿àáèéíñóÿ')
char_indices = {char: index for index, char in enumerate(chars)}
bptt = 100


@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == app.config['VERIFY_TOKEN']:
            return 'Verification token mismatch', 403
        return request.args['hub.challenge']
    return 'Improper verification request'


@app.route('/', methods=['POST'])
def webhook():
    for sender, message in messaging_events(request.get_json()):
        # get conversation history from cache
        print('Message from {0}: {1}'.format(sender, message))
        conversation = cache.get(sender) or '\ngrif:do you ever wonder why we\'re here?'
        message = '\nsimmons:' + message.lower() + ('' if message[-1] in '?!.' else '.') + '\ngrif:'
        if conversation.endswith(message): continue
        
        # send and cache model response
        response = get_response(conversation)
        print('Response to {0]: {1}'.format(sender, response))
        cache.set(sender, (conversation + response)[-bptt:])
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


def get_response(text, temp=0.8, max_len=250):
    if not text: return 'what?'
    len_seed = len(text)
    with graph.as_default():
        for i in range(max_len):
            if text[-1] == '\n': return text[len_seed:-1]
            indexed_text = [char_indices.get(char, 11) for char in text[-bptt:]]
            preds = model.predict(np.expand_dims(np.array(indexed_text), 0))[0][-1]
            preds = np.log(preds.clip(min=1e-5)) / temp
            preds = np.exp(preds) / np.sum(np.exp(preds))
            text += np.random.choice(chars, p=preds)
    return text + '...'


if __name__ == '__main__':
    text = ''
    while True:
        message = input('Say something: ')
        text += '\nsimmons:' + message.lower() + ('' if message[-1] in '?!.' else '.') + '\ngrif:'
        response = get_response(text)
        print(response)
        text += response
    # app.run(debug=True)
