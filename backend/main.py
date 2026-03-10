from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama as ol
app = FastAPI()

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Virtual Twin API is running 🔥"}

import json
import os
from fastapi import UploadFile, File

# Store uploaded messages here
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Load your messages from disk
    with open("../uploads/parsed_messages.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_messages = data['messages']
    
    # Pick 20 random messages as examples for now
    # We'll replace this with proper RAG in Phase 3
    import random
    examples = random.sample(all_messages, 20)
    examples_text = "\n".join([msg['message'] for msg in examples])
    
    # Build the prompt
    prompt = f"""You are Sudhamsh. Here are some real examples of how he texts:

{examples_text}

Now reply to this message exactly like Sudhamsh would. Short, casual, in his style:
"{request.message}"

Reply only with the message, nothing else."""

    # Send to Llama
    response = ol.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return {"reply": response['message']['content']}