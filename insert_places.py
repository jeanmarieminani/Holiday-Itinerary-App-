import argparse
from neo4j import GraphDatabase
import csv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neo4j connection details
URI = os.getenv("NEO4J_URI")
AUTH = tuple(os.getenv("NEO4J_AUTH").split('/'))

# Set up argument parsing
parser = argparse.ArgumentParser(description="Insert places into Neo4j from a CSV file")
parser.add_argument("csv_file_path", help="Path to the CSV file")
args = parser.parse_args()

csv_file_path = args.csv_file_path

def create_nodes_batch(tx, batch):
    """Create nodes in batches to improve performance."""
    for row in batch:
        tx.run(
            "CREATE (p:Place {id: $id, name: $name, type: $type, coordinates: [$longitude, $latitude]})",
            id=int(row['id']),
            name=row['name'],
            type=row['type'],
            longitude=float(row['longitude']),
            latitude=float(row['latitude'])
        )

def insert_csv_into_neo4j(uri, auth, csv_file_path):
    """Insert CSV data into Neo4j."""
    driver = GraphDatabase.driver(uri, auth=auth)

    # Count rows in CSV file
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        row_count = sum(1 for row in reader)

    with driver.session() as session:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append(row)
                if len(batch) >= 1000:  # Adjust batch size as needed
                    session.execute_write(create_nodes_batch, batch)
                    batch = []
            if batch:
                session.execute_write(create_nodes_batch, batch)

    driver.close()
    print(f"Nodes created successfully. Total nodes inserted: {row_count}")

    # Verify the number of nodes in Neo4j
    verify_node_count(uri, auth, row_count)

    # Create additional relationships and types
    driver = GraphDatabase.driver(uri, auth=auth)
    create_types(driver)
    create_relationships(driver, csv_file_path)
    create_close_to_relationships(driver)
    driver.close()

def verify_node_count(uri, auth, expected_count):
    """Verify the number of nodes in Neo4j."""
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        result = session.run("MATCH (p:Place) RETURN COUNT(p) AS count")
        count = result.single()["count"]
    driver.close()
    if count == expected_count:
        print(f"Verification successful. Total nodes in Neo4j: {count}")
    else:
        print(f"Verification failed. Expected nodes: {expected_count}, but found: {count}")

def create_types(driver):
    """Create Type nodes from a predefined list."""
    query = """
    WITH ["architecture", "art_galleries", "battlefields", "beaches", "burial_places", 
          "cathedrals", "catholic_churches", "cemeteries", "churches", "cultural", 
          "destroyed_objects", "gardens_and_parks", "geological_formations", "historic", 
          "historic_architecture", "historical_places", "installation", "interesting_places", 
          "monasteries", "monuments", "monuments_and_memorials", "mosques", "mountain_peaks", 
          "museums", "national_parks", "natural", "nature_reserves", "other", "other_beaches", 
          "other_burial_places", "other_churches", "other_museums", "other_nature_conservation_areas", 
          "other_temples", "religion", "sculptures", "tourist_object", "unclassified_objects", 
          "urban_environment", "view_points", "volcanoes", "water", "waterfalls"] AS types
    FOREACH (type IN types |
        MERGE (:Type {name: type})
    )
    """
    with driver.session() as session:
        session.run(query)
    print("Types created successfully.")

def create_relationships(driver, csv_file_path):
    """Create BELONGS_TO relationships between Place and Type nodes using local CSV data."""
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        with driver.session() as session:
            for row in reader:
                session.run(
                    """
                    MATCH (p:Place {id: $id})
                    MATCH (t:Type {name: $type})
                    MERGE (p)-[:BELONGS_TO]->(t)
                    """,
                    id=int(row['id']),
                    type=row['type']
                )
    print("BELONGS_TO relationships created successfully.")

def create_close_to_relationships(driver):
    """Create CLOSE_TO relationships between places within 2km distance."""
    query = """
    MATCH (p1:Place)
    MATCH (p2:Place)
    WHERE p1.id < p2.id
      AND size(p1.coordinates) = 2
      AND size(p2.coordinates) = 2
    WITH p1, p2,
         point({longitude: p1.coordinates[0], latitude: p1.coordinates[1]}) AS point1,
         point({longitude: p2.coordinates[0], latitude: p2.coordinates[1]}) AS point2
    WITH p1, p2, point.distance(point1, point2) AS distance
    WHERE distance <= 2000  // Distance in meters
    MERGE (p1)-[:CLOSE_TO {distance: distance}]->(p2)
    MERGE (p2)-[:CLOSE_TO {distance: distance}]->(p1)
    """
    with driver.session() as session:
        session.run(query)
    print("CLOSE_TO relationships created successfully.")

# Insert CSV data into Neo4j
insert_csv_into_neo4j(URI, AUTH, csv_file_path)
