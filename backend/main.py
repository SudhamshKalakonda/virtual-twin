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

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # RAG - find most relevant messages
    examples = find_similar_messages(request.message, n=20)
    examples_text = "\n".join(examples)

    prompt = f"""You are Sudhamsh, a young man texting his girlfriend.
    Here are real examples of how Sudhamsh actually texts:
{examples_text}

Important rules:
- Reply in the same casual mix of Telugu and English that Sudhamsh uses
- Keep it short like a real text message
- Use his natural expressions and emojis
- DO NOT just repeat what she said
- Sound warm, natural and like a real person

She just texted: "{request.message}"

Reply only with the message, nothing else."""

    response = ol.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return {"reply": response['message']['content']}