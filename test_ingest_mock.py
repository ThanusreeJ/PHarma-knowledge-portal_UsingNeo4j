import os
import random
from utils.neo4j_manager import Neo4jManager

def test_ingestion_mock():
    print("Starting mock ingestion test...")
    
    # Mock data
    filename = "mock_test.pdf"
    chunks = ["This is chunk 1", "This is chunk 2", "This is chunk 3"]
    # Mock embeddings (384 dimensions)
    embeddings = [[random.random() for _ in range(384)] for _ in chunks]
    
    print(f"Prepared {len(chunks)} chunks with mock embeddings.")

    neo = None
    try:
        print("Connecting to Neo4j...")
        neo = Neo4jManager()
        
        print("Creating vector index...")
        neo.create_vector_index()
        
        print("Adding document...")
        neo.add_document(filename, chunks, embeddings)
        
        print("✅ Mock ingestion successful!")
        
        # Verify
        print("Verifying count...")
        with neo.driver.session() as session:
            result = session.run("MATCH (n:Chunk) WHERE n.text STARTS WITH 'This is chunk' RETURN count(n) as count")
            count = result.single()["count"]
            print(f"ℹ️ Found {count} mock chunks in DB.")
            
    except Exception as e:
        print(f"❌ Error during mock ingestion: {e}")
    finally:
        if neo:
            neo.close()

if __name__ == "__main__":
    test_ingestion_mock()
