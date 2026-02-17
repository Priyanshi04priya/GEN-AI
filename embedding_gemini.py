import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

text = "The Cat Sat On The Mat"

response = client.models.embed_content(
    model="embedding-001",   
    contents=text
)

print("Vector Embedding:", response.embeddings[0].values)
