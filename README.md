# Grifbot
> Chat with Grif using the power of deep learning (Fan project)

Message Grifbot at [grifbot.cqcumbers.com/chat](https://grifbot.cqcumbers.com/chat), or add [grifchatbot](https://www.facebook.com/grifchatbot/) on facebook.

Grifbot uses [textgenrnn](https://github.com/minimaxir/textgenrnn)'s bidirectional word-level LSTM, fine-tuned on Red vs. Blue transcripts from roostertooths, to generate text in the style of an RvB episode. The bot seeds this model with a facebook messenger message and replies with the dialogue the model generates. Initially, grifbot used a character-level model that I trained from scratch, but due to limited data and computing power, output quality was very low. Fine-tuning an existing word-level model improves quality considerably, though you still shouldn't expect a coherent conversation.
