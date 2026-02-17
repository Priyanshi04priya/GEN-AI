from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
sentences = ['Hey, I am Priyanshi.', 'I am learning about embeddings.']

embeddings = model.encode(sentences)
print(embeddings)
