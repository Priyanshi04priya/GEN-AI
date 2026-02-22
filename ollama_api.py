from pyexpat.errors import messages
from urllib import response

from fastapi import FastAPI
from ollama import Client  
from fastapi import Body
from pydantic import BaseModel
app = FastAPI()
client = Client(
    host="http://localhost:11434"
)
client.pull('gemma3:1b')  # Pull the model to ensure it's available

class ChatRequest(BaseModel):
    message: str
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat(
        model="gemma3:1b",
        messages=[
            {"role": "user", "content": request.message}
        ]
    )
    return response['message']['content']

