import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the sentence transformer model for NLP
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(file_path):
    """Load project data from a CSV file."""
    return pd.read_csv(file_path)

def create_embeddings(data):
    """Generate embeddings for each attribute separately."""
    attributes = ['Project Name', 'Application Owner', 'SRE SPOC', 'Grafana URL', 'Splunk URL', 'SRE Score', 'SLI', 'SLO', 'Error Budget']
    embeddings_dict = {}
    for attr in attributes:
        embeddings_dict[attr] = model.encode(data[attr].astype(str).tolist(), convert_to_numpy=True)
    return embeddings_dict, data

def build_faiss_indexes(embeddings_dict):
    """Build FAISS indexes for each attribute."""
    index_dict = {}
    for attr, embeddings in embeddings_dict.items():
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        index_dict[attr] = index
    return index_dict

def get_best_match(query, index_dict, data):
    """Find the closest match across multiple attributes."""
    query_embedding = model.encode([query], convert_to_numpy=True)
    best_match = None
    best_distance = float('inf')
    best_attr = None
    best_index = None
    
    for attr, index in index_dict.items():
        distances, indices = index.search(query_embedding, 1)  # Find the closest match
        if distances[0][0] < best_distance:
            best_distance = distances[0][0]
            best_match = indices[0][0]
            best_attr = attr
    
    if best_distance < 1.0:  # Acceptable similarity threshold
        project_details = data.iloc[best_match]
        return f"{best_attr}: {project_details[best_attr]}"
    else:
        return "Sorry, I couldn't find relevant information. Please try rephrasing your query."

def chatbot():
    """NLP-powered chatbot interface that correctly understands any project-related query."""
    data = load_data('project_data.csv')
    embeddings_dict, data = create_embeddings(data)
    index_dict = build_faiss_indexes(embeddings_dict)
    
    print("\nWelcome to the NLP Project Info Chatbot! Type 'exit' to quit.\n")
    
    while True:
        query = input("Ask anything about the project data: ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = get_best_match(query, index_dict, data)
        print("\n" + response + "\n")

if __name__ == "__main__":
    chatbot()