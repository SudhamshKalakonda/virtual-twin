from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from embeddings import find_similar_messages, build_embeddings, build_conversation_embeddings, find_similar_conversations
from database import get_db, User
from auth import hash_password, verify_password, create_token, decode_token, generate_user_id
from groq import Groq
from dotenv import load_dotenv
import json
import os
import re

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SignupRequest(BaseModel):
    name: str
    whatsapp_name: str
    partner_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
def root():
    return {"message": "Virtual Twin API is running 🔥"}

@app.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=generate_user_id(),
        name=request.name,
        whatsapp_name=request.whatsapp_name,
        partner_name=request.partner_name,
        email=request.email,
        password=hash_password(request.password)
    )

    db.add(user)
    db.commit()

    token = create_token(user.id)
    return {"token": token, "name": user.name, "partner_name": user.partner_name}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id)
    return {"token": token, "name": user.name, "partner_name": user.partner_name}

@app.post("/upload")
async def upload_messages(
    file: UploadFile = File(...),
    token: str = "",
    db: Session = Depends(get_db)
):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    content = await file.read()
    text = content.decode('utf-8')

    pattern = re.compile(
        r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}[\s\u202f][AP]M)\]\s(.+?):\s(.+)'
    )

    user = db.query(User).filter(User.id == user_id).first()

    messages = []
    for line in text.split('\n'):
        match = pattern.match(line)
        if not match:
            continue
        date, time, sender, message = match.groups()
        if sender != user.whatsapp_name:
            continue
        if message.startswith('\u200e'):
            continue
        if 'image omitted' in message.lower():
            continue
        message = message.replace('<This message was edited>', '').strip()
        if not message:
            continue
        messages.append({'date': date, 'time': time, 'message': message})

    if not messages:
        raise HTTPException(status_code=400, detail="No messages found. Make sure your name matches exactly.")

    parsed = {'user': user.name, 'total_messages': len(messages), 'messages': messages}
    file_path = f"{UPLOAD_DIR}/{user_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    # Build single message embeddings
    build_embeddings(file_path, user_id)

    # Build conversation pair embeddings
    build_conversation_embeddings(text, user_id, user.whatsapp_name, user.partner_name)

    return {
        "message": "File uploaded and embeddings built ✅",
        "total_messages": len(messages)
    }

class ConversationMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    token: str
    history: list[ConversationMessage] = []

@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user_id = decode_token(request.token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Single message RAG
    examples = find_similar_messages(request.message, user_id=user_id, n=10)
    examples_text = "\n".join(examples)

    # Conversational RAG
    conv_examples = find_similar_conversations(request.message, user_id=user_id, n=5)
    conv_text = "\n".join([f"Her: {c['her']} → You: {c['you']}" for c in conv_examples])

    system_prompt = f"""You are {user.name}, texting his girlfriend {user.partner_name}.

Here are real examples of how {user.name} texts:
{examples_text}

Here are real examples of how {user.name} responded in similar conversations:
{conv_text}

STRICT RULES:
- Only reply based on the conversation context
- NEVER invent facts, events, or stories that weren't mentioned
- Keep replies short, 1-2 sentences max like real texting
- Use the same casual style shown in the examples
- Use emojis naturally like in the examples
- If you don't know something, respond casually like "haha idk" or "emo"
- DO NOT make up activities, events, or things that weren't discussed
- Sound like a real person texting, not an AI"""

    messages = [{'role': 'system', 'content': system_prompt}]
    for msg in request.history:
        messages.append({'role': msg.role, 'content': msg.content})
    messages.append({'role': 'user', 'content': request.message})

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=150
    )

    return {"reply": response.choices[0].message.content}