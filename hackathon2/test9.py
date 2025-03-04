import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the sentence transformer model for NLP
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(file_path):
    """Load project data from a CSV file."""
    return pd.read_csv(file_path)

def create_project_embeddings(data):
    """Generate embeddings for entire project details instead of individual attributes."""
    project_descriptions = data.apply(lambda row: f"Project Name: {row['Project Name']}, Application Owner: {row['Application Owner']}, SRE SPOC: {row['SRE SPOC']}, Grafana URL: {row['Grafana URL']}, Splunk URL: {row['Splunk URL']}, SRE Score: {row['SRE Score']}, SLI: {row['SLI']}%, SLO: {row['SLO']}%, Error Budget: {row['Error Budget']}", axis=1)
    project_embeddings = model.encode(project_descriptions.tolist(), convert_to_numpy=True)
    return project_embeddings, project_descriptions.tolist(), data

def build_faiss_index(project_embeddings):
    """Build a FAISS index for fast project similarity search."""
    dimension = project_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(project_embeddings)
    return index

def get_best_project_match(query, index, project_descriptions, data):
    """Find the best matching project for the query."""
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, 1)  # Find the closest project
    best_index = indices[0][0]
    
    if distances[0][0] < 1.0:  # Acceptable similarity threshold
        project_details = data.iloc[best_index]
        return project_details
    else:
        return None

def chatbot():
    """NLP-powered chatbot interface that correctly understands any project-related query."""
    data = load_data('project_data.csv')
    project_embeddings, project_descriptions, data = create_project_embeddings(data)
    index = build_faiss_index(project_embeddings)
    
    print("\nWelcome to the NLP Project Info Chatbot! Type 'exit' to quit.\n")
    
    while True:
        query = input("Ask anything about the project data: ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        project_details = get_best_project_match(query, index, project_descriptions, data)
        
        if project_details is not None:
            # Extract relevant information based on query intent
            if "grafana" in query.lower():
                response = f"Grafana URL: {project_details['Grafana URL']}"
            elif "splunk" in query.lower():
                response = f"Splunk URL: {project_details['Splunk URL']}"
            elif "sre score" in query.lower():
                response = f"SRE Score: {project_details['SRE Score']}"
            elif "sli" in query.lower():
                response = f"SLI: {project_details['SLI']}%"
            elif "slo" in query.lower():
                response = f"SLO: {project_details['SLO']}%"
            elif "error budget" in query.lower():
                response = f"Error Budget: {project_details['Error Budget']}"
            else:
                response = (f"Project Name: {project_details['Project Name']}\n"
                            f"Application Owner: {project_details['Application Owner']}\n"
                            f"SRE SPOC: {project_details['SRE SPOC']}\n"
                            f"Grafana URL: {project_details['Grafana URL']}\n"
                            f"Splunk URL: {project_details['Splunk URL']}\n"
                            f"SRE Score: {project_details['SRE Score']}\n"
                            f"SLI: {project_details['SLI']}%\n"
                            f"SLO: {project_details['SLO']}%\n"
                            f"Error Budget: {project_details['Error Budget']}")
        else:
            response = "Sorry, I couldn't find relevant information. Please try rephrasing your query."
        
        print("\n" + response + "\n")

if __name__ == "__main__":
    chatbot()
