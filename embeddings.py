from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
text="Hey, I am Priyanshi.', 'I am learning about embeddings."
response = client.embeddings.create(
    input=text,
    model="text-embedding-3-small"
)
print('Vector Embedding:', response.data[0].embedding)