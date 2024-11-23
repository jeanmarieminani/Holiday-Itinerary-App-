from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from pydantic_settings import BaseSettings

# The Settings class to load environment variables
class Settings(BaseSettings):
    neo4j_uri: str  # NEO4J_URI: Bolt protocol URI for Neo4j
    neo4j_auth: str  # NEO4J_AUTH: Format is "username/password"

    class Config:
        env_file = ".env"  # Specifies to load from a .env file

# Initialize settings from .env
settings = Settings()

# Extract Neo4j credentials from NEO4J_AUTH
try:
    neo4j_user, neo4j_password = settings.neo4j_auth.split("/")
except ValueError:
    raise RuntimeError("NEO4J_AUTH format should be 'username/password'.")

# Initialize the FastAPI app
app = FastAPI(title="vacation-in-france_fastapi")

# Connecting to Neo4j
driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(neo4j_user, neo4j_password)
)

# Startup event to check Neo4j connection
@app.on_event("startup")
def check_neo4j_connection():
    """
    Verify the connection to Neo4j when the application starts.
    """
    try:
        with driver.session() as session:
            session.run("RETURN 1")  # Simple query to verify connection
        print("Connected to Neo4j successfully.")
    except ServiceUnavailable as e:
        raise RuntimeError("Failed to connect to Neo4j. Ensure the database is running.") from e

# Shutdown event to close Neo4j connection
@app.on_event("shutdown")
def shutdown_event():
    """
    Close the Neo4j driver gracefully on shutdown.
    """
    driver.close()

# Basic root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Welcome to vacation-in-france_fastapi integrated with Neo4j db"}

# Retrieve nodes and relationships
@app.get("/nodes&relationships")
def get_all_nodes_and_relationships(limit: int = 25):
    """
    Fetch nodes and their relationships from Neo4j with a limit.
    """
    try:
        with driver.session() as session:
            result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT $limit", limit=limit)
            data = [
                {
                    "node1": record["n"],
                    "relationship": record["r"],
                    "node2": record["m"],
                }
                for record in result
            ]
            return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search for a place by name
@app.get("/search/place")
def search_place(name: str):
    """
    Search for a Place node containing the specified name.
    """
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (n:Place)
                WHERE n.name CONTAINS $name
                RETURN n.name AS name, n.id AS id, n.type AS type, n.coordinates AS coordinates
                """,
                name=name
            )
            places = [record.data() for record in result]
            if not places:
                raise HTTPException(status_code=404, detail=f"No places found containing '{name}'")
            return {"places": places}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Custom Cypher query endpoint
@app.post("/custom-query")
def run_custom_query(query: str):
    """
    Execute a custom Cypher query provided by the user.
    """
    try:
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            return {"result": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
