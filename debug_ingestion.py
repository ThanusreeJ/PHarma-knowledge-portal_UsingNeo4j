import os
from utils.rag_pipeline import ingest_document, process_pdf, chunk_text, generate_embeddings
from utils.neo4j_manager import Neo4jManager

def test_ingestion():
    file_path = os.path.join("data", "sample_clinical_trial.pdf")
    print(f"Testing ingestion with: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ Test file not found!")
        return

    # Mocking the file object for the existing process_pdf function
    # which expects a file-like object with .read() / .seek()
    with open(file_path, "rb") as f:
        # We need to manually call the steps to see where it breaks,
        # or just call ingest_document if we trust it handles 'f' correctly.
        # process_pdf in rag_pipeline.py does `reader = PdfReader(file)`.
        # pdf reader works with file objects.
        
        print("1. Extracting Text...")
        try:
             # We can't just pass 'f' to ingest_document safely because ingest_document 
             # might close it or the seek might behave differently if not handled right.
             # But let's try calling the pipeline functions step-by-step.
             
             text = process_pdf(f)
             print(f"   - Extracted {len(text)} characters.")
             if not text:
                 print("   ❌ Text extraction failed.")
                 return
        except Exception as e:
            print(f"   ❌ Error in process_pdf: {e}")
            return

        print("2. Chunking...")
        chunks = chunk_text(text)
        print(f"   - Created {len(chunks)} chunks.")
        
        print("3. Generating Embeddings...")
        try:
            embeddings = generate_embeddings(chunks)
            print(f"   - Generated {len(embeddings)} embeddings.")
        except Exception as e:
            print(f"   ❌ Error in embedding generation: {e}")
            return

        print("4. Uploading to Neo4j...")
        try:
            neo = Neo4jManager()
            neo.create_vector_index()
            neo.add_document("sample_clinical_trial.pdf", chunks, embeddings)
            neo.close()
            print("   ✅ Upload to Neo4j completed.")
        except Exception as e:
            print(f"   ❌ Error in Neo4j upload: {e}")

if __name__ == "__main__":
    test_ingestion()
