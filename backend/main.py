from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embeddings import find_similar_messages
import ollama as ol
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Virtual Twin API is running 🔥"}

@app.post("/upload")
async def upload_messages(file: UploadFile = File(...)):
    content = await file.read()
    messages = json.loads(content)
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    return {
        "message": "File uploaded successfully ✅",
        "total_messages": len(messages['messages']),
        "file_path": file_path
    }

class ConversationMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ConversationMessage] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    # RAG - find most relevant messages
    examples = find_similar_messages(request.message, n=20)
    examples_text = "\n".join(examples)

    system_prompt = f"""You are Sudhamsh, a young man texting his girlfriend.
Here are real examples of how Sudhamsh actually texts:

{examples_text}

    
STRICT RULES:
- Only reply based on the conversation context
- NEVER invent facts, events, or stories that weren't mentioned
- Keep replies short, 1-2 sentences max like real texting
- Use the same casual Telugu+English mix shown in the examples
- Use emojis naturally like in the examples
- If you don't know something, respond casually like "haha idk" or "emo"
- DO NOT make up activities, events, or things that weren't discussed
- Sound like a real person texting, not an AI"""

    # Build full conversation history for Llama
    messages = [{'role': 'system', 'content': system_prompt}]
    
    # Add previous conversation
    for msg in request.history:
        messages.append({'role': msg.role, 'content': msg.content})
    
    # Add current message
    messages.append({'role': 'user', 'content': request.message})

    response = ol.chat(
        model='llama3.2',
        messages=messages
    )

    return {"reply": response['message']['content']}