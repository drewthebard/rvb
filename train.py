from textgenrnn import textgenrnn

textgen = textgenrnn(name="textgenrnn_model")
textgen.train_from_file('script.txt', num_epochs=100, new_model=True, word_level=True, rnn_bidirectional=True, dim_embeddings=300)
textgen.generate(100, temperature=1.0)
