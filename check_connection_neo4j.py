from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

URI = "bolt://localhost:7272"
AUTH = os.getenv("NEO4J_AUTH")

if not AUTH:
    raise ValueError("NEO4J_AUTH environment variable is not set")

# Split the auth variable to pass username and password separately
username, password = AUTH.split('/')

try:
    with GraphDatabase.driver(URI, auth=(username, password)) as driver:
        driver.verify_connectivity()
        print("Connection verified successfully!")
except Exception as e:
    print(f"An error occurred: {e}")

