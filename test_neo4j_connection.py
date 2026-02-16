import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

print(f"Attempting to connect to Neo4j at {uri} with user {user}...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Connection successful!")
    
    with driver.session() as session:
        # Test Write
        print("Testing write permission...")
        session.run("CREATE (n:TestNode {id: 'test', message: 'Hello Neo4j'})")
        print("✅ Write successful!")
        
        # Test Read
        print("Testing read...")
        result = session.run("MATCH (n:TestNode) RETURN n.message AS msg")
        msg = result.single()["msg"]
        print(f"✅ Read successful: {msg}")
        
        # Cleanup
        session.run("MATCH (n:TestNode) DELETE n")
        print("✅ Cleanup successful!")
        
        # Check for Chunks
        result = session.run("MATCH (n:Chunk) RETURN count(n) AS count")
        count = result.single()["count"]
        print(f"ℹ️ Current Chunk count in DB: {count}")

    driver.close()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting Tips:")
    print("1. Is the Podman container running? (Run 'podman ps')")
    print("2. Are the ports 7474 and 7687 mapped correctly?")
    print("3. Did you change the password? Check your .env file.")
