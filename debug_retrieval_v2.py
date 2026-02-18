print("Importing modules...")
import time
from utils.neo4j_manager import Neo4jManager
# Delay importing sentence_transformers to see if that's the slow part
print("Modules imported. Loading model...")

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

def debug_query():
    query = "List all the secondary objectives and their corresponding endpoints."
    with open("debug_results_v3.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")

        log(f"Query: {query}")
        
        start = time.time()
        query_embedding = model.encode([query])[0].tolist()
        log(f"Embedding generated in {time.time() - start:.2f}s")
        
        log("Connecting to Neo4j...")
        neo = Neo4jManager()
        
        log("running vector search (top_k=15)...")
        results = neo.query_similar_chunks(query_embedding, top_k=15)
        log(f"Got {len(results)} results.")
        
        found_objectives = False
        found_endpoints = False
        
        for i, res in enumerate(results):
            score = res.get('score', 0)
            text = res.get('text', '')
            index = res.get('index', 'N/A')
            log(f"\n#{i+1} [Score: {score:.4f}] [Index: {index}]")
            log(f"Text Preview: {text[:100]}...")
            
            if "Secondary Objectives" in text:
                log(">>> FOUND OBJECTIVES HERE <<<")
                found_objectives = True
            if "Secondary Endpoints" in text:
                log(">>> FOUND ENDPOINTS HERE <<<")
                found_endpoints = True

        if not found_objectives:
            log("\n❌ MISSING: 'Secondary Objectives' section not found in top 15.")
        if not found_endpoints:
            log("\n❌ MISSING: 'Secondary Endpoints' section not found in top 15.")

        neo.close()

if __name__ == "__main__":
    debug_query()
