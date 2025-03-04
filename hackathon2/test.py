import pandas as pd
from fuzzywuzzy import process

def load_data(file_path):
    """Load project data from a CSV file."""
    return pd.read_csv(file_path)

def find_best_match(query, choices):
    """Find the closest match for a query from a list of choices."""
    best_match, score = process.extractOne(query, choices)
    return best_match if score > 70 else None  # Only return if confidence is high

def get_project_info(data, project_name):
    """Retrieve project details based on the name."""
    match = find_best_match(project_name, data['Project Name'].tolist())
    
    if match:
        project_details = data[data['Project Name'] == match].iloc[0]
        response = (f"Project Name: {project_details['Project Name']}\n"
                    f"Application Owner: {project_details['Application Owner']}\n"
                    f"SRE SPOC: {project_details['SRE SPOC']}\n"
                    f"Grafana URL: {project_details['Grafana URL']}\n"
                    f"Splunk URL: {project_details['Splunk URL']}\n"
                    f"SRE Score: {project_details['SRE Score']}\n"
                    f"SLI: {project_details['SLI']}%\n"
                    f"SLO: {project_details['SLO']}%\n"
                    f"Error Budget: {project_details['Error Budget']}")
        return response
    else:
        return "Sorry, no matching project found."

def chatbot():
    """Simple command-line chatbot interface."""
    data = load_data('project_data.csv')
    print("\nWelcome to the Project Info Chatbot! Type 'exit' to quit.\n")
    
    while True:
        query = input("Ask about a project: ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = get_project_info(data, query)
        print("\n" + response + "\n")

if __name__ == "__main__":
    chatbot()
