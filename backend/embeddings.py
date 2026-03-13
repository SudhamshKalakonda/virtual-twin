import chromadb
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="../vectordb")

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