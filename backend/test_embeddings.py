from embeddings import build_embeddings, find_similar_messages

# Build embeddings for all your messages
build_embeddings("../uploads/parsed_messages.json")

# Test similarity search
print("\nTesting similarity search...")
results = find_similar_messages("what are you doing?")
print("\nMost similar messages from your history:")
for msg in results:
    print(f"- {msg}")