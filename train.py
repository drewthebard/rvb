from textgenrnn import textgenrnn
import os

new_model = not os.path.isfile('model_config.json')

if not new_model:
    model = textgenrnn(
        weights_path='model_weights.hdf5',
        vocab_path='model_vocab.json',
        config_path='model_config.json',
    )
else:
    model = textgenrnn(name='model')

model.train_from_file(
    'scripts.txt',
    num_epochs=500,
    new_model=new_model,
    word_level=True,
    rnn_bidirectional=True,
    dim_embeddings=300
)
