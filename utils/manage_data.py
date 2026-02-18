import os
from utils.neo4j_manager import Neo4jManager
from utils.rag_pipeline import chunk_text, generate_embeddings
from pypdf import PdfReader

def clean_database():
    print("Connecting to Neo4j...")
    neo = Neo4jManager()
    print("Deleting all nodes and relationships...")
    
    # Delete all nodes and relationships
    query = "MATCH (n) DETACH DELETE n"
    with neo.driver.session() as session:
        session.run(query)
        
    # Verify
    count_query = "MATCH (n) RETURN count(n) as count"
    with neo.driver.session() as session:
        result = session.run(count_query)
        count = result.single()["count"]
        print(f"Database cleaned. Current node count: {count}")
    
    neo.close()

def ingest_complex_pdf():
    pdf_path = os.path.join("data", "complex_clinical_protocol.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Please generate it first.")
        return

    print(f"Processing {pdf_path}...")
    
    # Extract text
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        print(f"Text extracted. Length: {len(text)} chars")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    # Chunk
    chunks = chunk_text(text)
    print(f"Generated {len(chunks)} chunks.")

    # Embed
    print("Generating embeddings (this may take a moment)...")
    embeddings = generate_embeddings(chunks)
    print("Embeddings generated.")

    # Ingest
    print("Ingesting into Neo4j...")
    neo = Neo4jManager()
    neo.create_vector_index()
    neo.add_document("complex_clinical_protocol.pdf", chunks, embeddings)
    neo.close()
    print("Ingestion complete!")

if __name__ == "__main__":
    choice = input("Enter 'clean' to wipe DB, 'ingest' to load PDF, or 'all' for both: ").strip().lower()
    
    if choice in ['clean', 'all']:
        clean_database()
    
    if choice in ['ingest', 'all']:
        ingest_complex_pdf()
