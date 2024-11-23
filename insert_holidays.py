from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import argparse
import json

# Load environment variables from .env file
load_dotenv()

# Neo4j connection details
URI = os.getenv("NEO4J_URI")
AUTH = tuple(os.getenv("NEO4J_AUTH").split('/'))

def insert_json_into_neo4j(uri, auth, data, label, fields):
    driver = GraphDatabase.driver(uri, auth=auth)

    # Create query dynamically based on provided fields
    query = f"""
    CREATE (n:{label} {{
        {', '.join([f"{field}: ${field}" for field in fields])}
    }})
    """

    with driver.session() as session:
        for entry in data:
            params = {field: entry[field] for field in fields}
            print(f"Inserting: {params}")  # Debug statement to print the data being inserted
            session.run(query, **params)

    driver.close()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Insert holiday data into Neo4j from a JSON file")
    parser.add_argument("json_file_path", help="Path to the JSON file containing holiday data")
    args = parser.parse_args()

    # Read the JSON file
    with open(args.json_file_path, 'r', encoding='utf-8') as f:
        holidays_json = json.load(f)

    # Fields to be included in the Neo4j nodes
    fields = ["Holiday_name", "EnglishName", "Date", "Type", "Description", "WhatToDo"]

    # Insert holiday data into Neo4j
    insert_json_into_neo4j(URI, AUTH, holidays_json, "Holiday", fields)
    print("Holiday data inserted successfully!")
