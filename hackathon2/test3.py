import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the sentence transformer model for NLP
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(file_path):
    """Load project data from a CSV file."""
    return pd.read_csv("project_data.csv")

def create_embeddings(data):
    """Generate embeddings for project details."""
    descriptions = data.apply(lambda row: f"Project Name: {row['Project Name']}, Application Owner: {row['Application Owner']}, SRE SPOC: {row['SRE SPOC']}, Grafana URL: {row['Grafana URL']}, Splunk URL: {row['Splunk URL']}, SRE Score: {row['SRE Score']}, SLI: {row['SLI']}%, SLO: {row['SLO']}%, Error Budget: {row['Error Budget']}", axis=1)
    embeddings = model.encode(descriptions.tolist(), convert_to_numpy=True)
    return embeddings, descriptions.tolist(), data
def build_faiss_index(embeddings):
    """Build a FAISS index for fast similarity search."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def get_best_match(query, index, descriptions, data):
    """Retrieve the best matching project data based on query."""
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, 1)  # Find the closest match
    best_index = indices[0][0]
    
    if distances[0][0] < 1.0:  # Acceptable similarity threshold
        project_details = data.iloc[best_index]
        return (f"Project Name: {project_details['Project Name']}\n"
                f"Application Owner: {project_details['Application Owner']}\n"
                f"SRE SPOC: {project_details['SRE SPOC']}\n"
                f"Grafana URL: {project_details['Grafana URL']}\n"
                f"Splunk URL: {project_details['Splunk URL']}\n"
                f"SRE Score: {project_details['SRE Score']}\n"
                f"SLI: {project_details['SLI']}%\n"
                f"SLO: {project_details['SLO']}%\n"
                f"Error Budget: {project_details['Error Budget']}")
    else:
        return "Sorry, I couldn't find relevant information. Please try rephrasing your query."

def chatbot():
    """NLP-powered chatbot interface that can answer any project-related query."""
    data = load_data('project_data.csv')
    embeddings, descriptions, data = create_embeddings(data)
    index = build_faiss_index(embeddings)
    
    print("\nWelcome to the NLP Project Info Chatbot! Type 'exit' to quit.\n")
    
    while True:
        query = input("Ask anything about the project data: ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = get_best_match(query, index, descriptions, data)
        print("\n" + response + "\n")

if __name__ == "__main__":
    chatbot()
