from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
text="The Cat Sat On The Mat"
response = client.embeddings.create(
    input=text,
    model="text-embedding-3-small"
)
print('Vector Embedding:', response.data[0].embedding)