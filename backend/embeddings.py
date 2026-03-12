from sentence_transformers import SentenceTransformer
import chromadb
import json

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB
client = chromadb.PersistentClient(path="../vectordb")
collection = client.get_or_create_collection(name="messages")

def build_embeddings(messages_path: str):
    # Load your parsed messages
    with open(messages_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    
    print(f"Building embeddings for {len(messages)} messages...")
    
    # Process in batches of 500
    batch_size = 500
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        
        texts = [msg['message'] for msg in batch]
        ids = [str(i + j) for j in range(len(batch))]
        
        # Convert messages to vectors
        embeddings = model.encode(texts).tolist()
        
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"Processed {min(i + batch_size, len(messages))}/{len(messages)}")
    
    print("Done")

def find_similar_messages(query: str, n: int = 20):
    # Convert the query to a vector
    query_embedding = model.encode(query).tolist()
    
    # Find the most similar messages
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n
    )
    
    return results['documents'][0]