import tiktoken
#Encoding
encoder=tiktoken.encoding_for_model("gpt-4o")
print('Vocab size:', encoder.n_vocab)

text="Hey, I'm Priyanshi."
print('Text:', text)
tokens=encoder.encode(text)
print('Tokens:', tokens)

#Decoding
my_tokens= [25216, 11, 5477, 37358, 121378, 3686, 13]
decoded=encoder.decode(my_tokens)
print('Decoded:', decoded)
