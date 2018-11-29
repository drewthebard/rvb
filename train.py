from textgenrnn import textgenrnn

textgen = textgenrnn()
textgen.train_from_file('script.txt', num_epochs=20000)
textgen.generate(100, temperature=1.0)
