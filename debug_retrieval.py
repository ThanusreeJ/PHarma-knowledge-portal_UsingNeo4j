from utils.rag_pipeline import get_embedding_model
from utils.neo4j_manager import Neo4jManager

def debug_query():
    query = "List all the secondary objectives and their corresponding endpoints."
    print(f"Query: {query}")
    
    model = get_embedding_model()
    query_embedding = model.encode([query])[0].tolist()
    
    neo = Neo4jManager()
    
    print("\n--- Top 10 Chunks ---")
    # We call query_similar_chunks directly to see raw results
    results = neo.query_similar_chunks(query_embedding, top_k=10)
    
    for i, res in enumerate(results):
        score = res.get('score', 0)
        text = res.get('text', '')[:200].replace('\n', ' ') # Preview first 200 chars
        index = res.get('index', 'N/A')
        print(f"#{i+1} [Score: {score:.4f}] [Index: {index}]: {text}...")

    neo.close()

if __name__ == "__main__":
    debug_query()
