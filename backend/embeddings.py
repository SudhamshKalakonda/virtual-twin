import chromadb
import json
import re
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="../vectordb")

# ─── Single Message RAG (existing) ────────────────────────
def get_collection(user_id: str):
    return client.get_or_create_collection(name=f"messages_{user_id}")

def build_embeddings(messages_path: str, user_id: str):
    with open(messages_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data['messages']
    collection = get_collection(user_id)

    print(f"Building embeddings for {len(messages)} messages...")

    batch_size = 500
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        texts = [msg['message'] for msg in batch]
        ids = [str(i + j) for j in range(len(batch))]
        embeddings = model.encode(texts).tolist()
        collection.add(documents=texts, embeddings=embeddings, ids=ids)
        print(f"Processed {min(i + batch_size, len(messages))}/{len(messages)}")

    print("Done! ✅")

def find_similar_messages(query: str, user_id: str, n: int = 20) -> list:
    collection = get_collection(user_id)
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n)
    return results['documents'][0]

# ─── Conversational RAG (new) ─────────────────────────────
def get_conversation_collection(user_id: str):
    return client.get_or_create_collection(name=f"conversations_{user_id}")

def parse_conversation_pairs(raw_text: str, your_name: str, her_name: str) -> list:
    pattern = re.compile(
        r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}[\s\u202f][AP]M)\]\s(.+?):\s(.+)'
    )

    all_messages = []
    for line in raw_text.split('\n'):
        match = pattern.match(line)
        if not match:
            continue
        date, time, sender, message = match.groups()
        if message.startswith('\u200e'):
            continue
        if 'image omitted' in message.lower():
            continue
        message = message.replace('<This message was edited>', '').strip()
        if not message:
            continue
        all_messages.append({'sender': sender, 'message': message})

    # Extract her message → your reply pairs
    pairs = []
    for i in range(len(all_messages) - 1):
        current = all_messages[i]
        next_msg = all_messages[i + 1]

        if current['sender'] == her_name and next_msg['sender'] == your_name:
            input_msg = current['message'].strip()
            output_msg = next_msg['message'].strip()

            if len(input_msg) < 2 or len(output_msg) < 2:
                continue
            if len(input_msg) > 300 or len(output_msg) > 300:
                continue

            pairs.append({
                'input': input_msg,
                'output': output_msg,
                'combined': f"Her: {input_msg} | You: {output_msg}"
            })

    return pairs

def build_conversation_embeddings(raw_text: str, user_id: str, your_name: str, her_name: str):
    pairs = parse_conversation_pairs(raw_text, your_name, her_name)
    collection = get_conversation_collection(user_id)

    print(f"Building conversation embeddings for {len(pairs)} pairs...")

    batch_size = 500
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        texts = [pair['combined'] for pair in batch]
        ids = [f"conv_{i + j}" for j in range(len(batch))]
        embeddings = model.encode(texts).tolist()
        collection.add(documents=texts, embeddings=embeddings, ids=ids)
        print(f"Processed {min(i + batch_size, len(pairs))}/{len(pairs)}")

    print("Conversation embeddings done! ✅")

def find_similar_conversations(query: str, user_id: str, n: int = 10) -> list:
    collection = get_conversation_collection(user_id)
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n)

    # Extract just YOUR responses from the pairs
    responses = []
    for doc in results['documents'][0]:
        # Format: "Her: X | You: Y"
        if '| You: ' in doc:
            your_response = doc.split('| You: ')[1].strip()
            her_message = doc.split('Her: ')[1].split(' | You:')[0].strip()
            responses.append({
                'her': her_message,
                'you': your_response
            })

    return responses