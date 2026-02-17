from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Hey, How are you?"
)
print(response.text)
