import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

folder_path = "myapp/rag_Jina/model_data"
data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                curr = json.load(f)
                data.extend(curr)
            except json.JSONDecodeError as e:
                print(f"Error decoding {file_path}: {e}")

texts = [json.dumps(item, ensure_ascii=False) for item in data]
model = SentenceTransformer('all-MiniLM-L6-v2')

print("model is loaded")

# # Get embeddings
# embeddings = model.encode(texts)
# print(f"Embedding shape: {embeddings.shape}")

# # Initialize FAISS index
# dimension = embeddings.shape[1]
# quantizer = faiss.IndexFlatL2(dimension)
# index = faiss.IndexIVFFlat(quantizer, dimension, 50)
# index.train(np.array(embeddings).astype('float32'))
# index.add(np.array(embeddings).astype('float32'))

# faiss.write_index(index, "json_faiss.index")

# Get embeddings
embeddings = model.encode(texts)
print(f"Embedding shape: {embeddings.shape}")

# Initialize FAISS index
dimension = embeddings.shape[1]
embeddings = np.array(embeddings).astype('float32')

if len(embeddings) >= 50:
    nlist = min(50, len(embeddings) // 5)
    print(f"Using IVF index with nlist = {nlist}")
    quantizer = faiss.IndexFlatL2(dimension)
    index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    index.train(embeddings)
else:
    print("Too few embeddings, using Flat index instead.")
    index = faiss.IndexFlatL2(dimension)

index.add(embeddings)
faiss.write_index(index, "json_faiss.index")

with open("myapp/rag_Jina/json_data_backup.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Function to query the data
def query_json(user_query, k=1):
    query_embedding = model.encode([user_query])
    
    distances, indices = index.search(query_embedding, k)
    
    results = []
    for i in range(min(k, len(indices[0]))):
        idx = indices[0][i]
        results.append(data[idx])  # Retrieve the data entry
    return results

user_query = input("Question: ")

results = query_json(user_query)

print("Related answers:")
for i, item in enumerate(results):
    print(f"\nTop {i+1}:")
    print(json.dumps(item, ensure_ascii=False, indent=2))

