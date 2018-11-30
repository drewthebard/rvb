import os
from textgenrnn import textgenrnn

new_model = not os.path.isfile('weights.hdf5')

if not new_model:
    model = textgenrnn(
        weights_path='weights.hdf5',
        vocab_path='vocab.json',
        config_path='config.json',
    )
else:
    model = textgenrnn(name='')

model.train_from_file(
    'scripts.txt',
    num_epochs=100,
    new_model=new_model,
    word_level=True,
    rnn_bidirectional=True,
    dim_embeddings=300
)
