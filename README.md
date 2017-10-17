# Grifbot
Chat with Grif from RvB on facebook messenger, using the power of deep learning. Entirely unofficial

Actual model architecture and training code is in fastai-notes repository. Nothing too fancy, just a 3-layer LSTM in keras trained on character embeddings from Red vs. Blue transcripts (courtesy of roostertooths.com). This project simply seeds the model with a message from facebook messenger, appends `GRIF: `, and replies with the dialogue the model generates. Due to the limited training data output may be rather incoherent, but I suppose it's part of the charm.
