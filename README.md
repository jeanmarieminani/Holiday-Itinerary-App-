Welcome to the Vacation in France FastAPI integrated with Neo4j database   -Open-source project 

**Project documentation, installation steps, 
usage instructions, and any other relevant information**

**Overview**
The main purpose of this project is to build  a FastAPI-based backend integrated with a 
Neo4j graph database to manage and query vacation-related data such as places, relationships, and more.
The API is designed to be scalable, secure, and performant for handling graph-based queries.

**Features**
FastAPI Framework for rapid development and API documentation.
Neo4j Integration for powerful graph database queries.
Endpoints for:
Retrieving nodes and relationships.
Searching for specific places by name.
Running custom Cypher queries.
Dockerized Setup for easy deployment and environment consistency.

**Requirements**
Ensure the following tools are installed on your system:
Python 3.8+
Docker
Docker Compose

**Setup Instructions**
1. Clone the Repository
git clone https://github.com/jeanmarieminani/Holiday-Itinerary-App-
cd france_neo4j_newdb

2. Create a .env File
Create a .env file in the root directory with the following variables:
NEO4J_URI=bolt://localhost:7272
NEO4J_AUTH=user/your_password

3. Start Neo4j with Docker Compose
docker-compose up -d

After starting the Neo4j database containe, map the Bolt protocol to port 7272 
and the HTTP interface to port 7171.
Access the Neo4j browser at: http://127.0.0.1:7171/browser/

4. Set Up Python Virtual Environment
python3 -m venv france_env
source france_env/bin/activate
pip install -r requirements.txt

5. Run the FastAPI Application
uvicorn main:app --host 127.0.0.1 --port 9090 --reload
Access the FastAPI documentation at: http://127.0.0.1:9090/docs

**Endpoints**

1. Health Check
GET /
Response: { "message": "Welcome to vacation-in-france_fastapi integrated with Neo4j db" }
    
2. Retrieve Nodes and Relationships
GET /nodes&relationships
Query Params: limit (optional, default: 25)
Response: Nodes and their relationships.
    
3. Search for a Place
GET /search/place
Query Params: name (partial match for place names)
Response: Place details including id, type, and coordinates.
    
4. Custom Cypher Query
POST /custom-query
Request Body: { "query": "<Your Cypher Query>" }
Response: Query results.

**Technologies Used**
FastAPI: High-performance Python web framework.
Neo4j: Graph database for managing connected data.
Docker & Docker Compose: For containerized deployment.
Pydantic Settings: For environment variable management.
    
**Troubleshooting**
1. Port Already in Use
Stop any processes using the required ports:
sudo lsof -i :7171
sudo lsof -i :7272
sudo lsof -i :9090
Kill the processes using their PID:
kill -9 <PID>

2. Neo4j Connection Issues
Verify the Neo4j container is running:
docker ps
Check logs for errors: 
docker logs neo4j_newdb
docker logs neo4j_newdb

3. FastAPI Errors
Check Python dependencies:
pip install -r requirements.txt

**License**
This project is licensed under the MIT License.

**Contributors**
Jean-Marie Vianney Minani - https://github.com/jeanmarieminani
Sabina Kolliwer  - https://github.com/sabinako
    
Contributions are welcome! Feel free to open issues or submit pull requests.
