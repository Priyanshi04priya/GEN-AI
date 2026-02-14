import tiktoken
encoder=tiktoken.encoding_for_model("gpt-4o")
print('Vocab size:', encoder.n_vocab)

text="The Cat Sat On The Mat"
print('Text:', text)
tokens=encoder.encode(text)
print('Tokens:', tokens)

my_tokens=[976, 19288, 22232, 2160, 623, 9926]
decoded=encoder.decode(my_tokens)
print('Decoded:', decoded)
