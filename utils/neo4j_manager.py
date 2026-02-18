import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import hashlib

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.verify_connectivity()
        except Exception as e:
            logger.error(f"Failed to create Neo4j driver: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def verify_connectivity(self):
        try:
            self.driver.verify_connectivity()
            logger.info("Connected to Neo4j successfully.")
        except Exception as e:
            logger.error(f"Could not connect to Neo4j: {e}")
            raise

    def create_vector_index(self):
        """Creates a vector index on Chunk nodes if it doesn't exist."""
        check_query = "SHOW INDEXES YIELD name WHERE name = 'chunk_embeddings' RETURN count(*) as count"
        
        create_query = """
        CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 384,
         `vector.similarity_function`: 'cosine'
        }}
        """
        try:
            with self.driver.session() as session:
                result = session.run(check_query)
                count = result.single()["count"]
                if count > 0:
                    logger.info("Vector index 'chunk_embeddings' already exists. Skipping creation.")
                    return

                logger.info("Creating vector index 'chunk_embeddings'...")
                session.run(create_query)
                logger.info("Vector index creation command sent.")
        except Exception as e:
            logger.error(f"Error checking/creating vector index: {e}")

    def _compute_file_hash(self, filename: str, content_preview: str = "") -> str:
        """Compute a hash for deduplication"""
        hash_input = f"{filename}_{content_preview[:500]}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def add_document(self, filename: str, chunks: List[str], embeddings: List[List[float]], 
                     doc_type: str = "unknown", entities_per_chunk: Optional[List[Dict]] = None):
        """
        Adds a document and its chunks to the graph with entity extraction.
        
        Args:
            filename (str): Name of the file.
            chunks (list of str): Text content of chunks.
            embeddings (list of list of floats): Embeddings for each chunk.
            doc_type (str): Type of document (clinical_trial, research_paper, etc.)
            entities_per_chunk (list of dict): Entities extracted for each chunk
        """
        file_hash = self._compute_file_hash(filename, chunks[0] if chunks else "")
        
        # Check if document already exists
        check_query = "MATCH (d:Document {file_hash: $hash}) RETURN count(d) as count"
        try:
            with self.driver.session() as session:
                result = session.run(check_query, hash=file_hash)
                if result.single()["count"] > 0:
                    logger.warning(f"Document '{filename}' already exists (same hash). Skipping.")
                    return
        except Exception as e:
            logger.error(f"Error checking for duplicate: {e}")
        
        # Create document and chunks
        query = """
        CREATE (d:Document {
            filename: $filename,
            upload_date: datetime(),
            doc_type: $doc_type,
            file_hash: $file_hash,
            chunk_count: size($chunks)
        })
        WITH d
        UNWIND range(0, size($chunks)-1) AS i
        CREATE (c:Chunk {
            text: $chunks[i],
            embedding: $embeddings[i],
            chunk_index: i
        })
        MERGE (d)-[:HAS_CHUNK]->(c)
        WITH c, i, d
        ORDER BY i
        WITH d, collect(c) as chunk_nodes
        FOREACH (j in range(0, size(chunk_nodes)-2) |
            FOREACH (c1 in [chunk_nodes[j]] |
                FOREACH (c2 in [chunk_nodes[j+1]] |
                    MERGE (c1)-[:NEXT]->(c2)
                )
            )
        )
        RETURN d, chunk_nodes
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, filename=filename, chunks=chunks, 
                                   embeddings=embeddings, doc_type=doc_type, file_hash=file_hash)
                result.consume()
                
                # Add entities if provided
                if entities_per_chunk:
                    self._add_entities_to_chunks(filename, chunks, entities_per_chunk)
                
            logger.info(f"Document '{filename}' added with {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise

    def _add_entities_to_chunks(self, filename: str, chunks: List[str], entities_per_chunk: List[Dict]):
        """Add entity nodes and MENTIONS relationships"""
        try:
            with self.driver.session() as session:
                for chunk_idx, entities_dict in enumerate(entities_per_chunk):
                    for entity_type, entity_list in entities_dict.items():
                        for entity_name in entity_list:
                            # Create/merge entity and link to chunk
                            query = """
                            MATCH (d:Document {filename: $filename})-[:HAS_CHUNK]->(c:Chunk {chunk_index: $chunk_idx})
                            MERGE (e:Entity {name: $entity_name, type: $entity_type})
                            ON CREATE SET e.mentions_count = 1
                            ON MATCH SET e.mentions_count = e.mentions_count + 1
                            MERGE (c)-[:MENTIONS]->(e)
                            """
                            session.run(query, filename=filename, chunk_idx=chunk_idx, 
                                      entity_name=entity_name, entity_type=entity_type)
            logger.info(f"Added entities for document '{filename}'")
        except Exception as e:
            logger.error(f"Error adding entities: {e}")

    def create_cross_document_links(self, similarity_threshold: float = 0.75):
        """
        Create SIMILAR_TO relationships between chunks from different documents.
        Uses cosine similarity of embeddings.
        """
        query = """
        MATCH (c1:Chunk)<-[:HAS_CHUNK]-(d1:Document)
        MATCH (c2:Chunk)<-[:HAS_CHUNK]-(d2:Document)
        WHERE d1.filename < d2.filename  // Avoid duplicates and self-links
        AND c1.embedding IS NOT NULL AND c2.embedding IS NOT NULL
        WITH c1, c2, 
             gds.similarity.cosine(c1.embedding, c2.embedding) AS similarity
        WHERE similarity >= $threshold
        MERGE (c1)-[s:SIMILAR_TO]->(c2)
        SET s.score = similarity
        RETURN count(s) as relationships_created
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, threshold=similarity_threshold)
                count = result.single()["relationships_created"]
                logger.info(f"Created {count} cross-document SIMILAR_TO relationships")
                return count
        except Exception as e:
            logger.error(f"Error creating cross-document links: {e}")
            # Fallback: use manual cosine similarity calculation
            return self._create_cross_doc_links_manual(similarity_threshold)

    def _create_cross_doc_links_manual(self, similarity_threshold: float = 0.75):
        """Fallback method using Python-based similarity computation"""
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        try:
            with self.driver.session() as session:
                # Get all chunks with embeddings grouped by document
                query = """
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WHERE c.embedding IS NOT NULL
                RETURN id(c) as chunk_id, c.embedding as embedding, d.filename as doc
                """
                result = session.run(query)
                chunks_data = [(record["chunk_id"], np.array(record["embedding"]), record["doc"]) 
                              for record in result]
                
                if len(chunks_data) < 2:
                    logger.warning("Not enough chunks for cross-document linking")
                    return 0
                
                # Group by document
                doc_chunks = {}
                for chunk_id, embedding, doc in chunks_data:
                    if doc not in doc_chunks:
                        doc_chunks[doc] = []
                    doc_chunks[doc].append((chunk_id, embedding))
                
                # Compare chunks across different documents
                relationship_count = 0
                doc_names = list(doc_chunks.keys())
                
                for i in range(len(doc_names)):
                    for j in range(i + 1, len(doc_names)):
                        doc1_chunks = doc_chunks[doc_names[i]]
                        doc2_chunks = doc_chunks[doc_names[j]]
                        
                        # Compute similarities
                        for chunk1_id, emb1 in doc1_chunks:
                            for chunk2_id, emb2 in doc2_chunks:
                                similarity = cosine_similarity([emb1], [emb2])[0][0]
                                
                                if similarity >= similarity_threshold:
                                    # Create relationship
                                    create_rel_query = """
                                    MATCH (c1:Chunk), (c2:Chunk)
                                    WHERE id(c1) = $id1 AND id(c2) = $id2
                                    MERGE (c1)-[s:SIMILAR_TO]->(c2)
                                    SET s.score = $score
                                    """
                                    session.run(create_rel_query, id1=chunk1_id, id2=chunk2_id, score=float(similarity))
                                    relationship_count += 1
                
                logger.info(f"Created {relationship_count} cross-document relationships (manual method)")
                return relationship_count
        except Exception as e:
            logger.error(f"Error in manual cross-document linking: {e}")
            return 0

    def get_documents(self) -> List[Dict[str, Any]]:
        """Get list of all documents in the graph"""
        query = """
        MATCH (d:Document)
        OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
        RETURN d.filename as filename, d.upload_date as upload_date, 
               d.doc_type as doc_type, count(c) as chunk_count
        ORDER BY d.upload_date DESC
        """
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return []

    def delete_document(self, filename: str):
        """Delete a document and all its related nodes"""
        query = """
        MATCH (d:Document {filename: $filename})
        OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
        OPTIONAL MATCH (c)-[r]-()
        DELETE r, c, d
        """
        try:
            with self.driver.session() as session:
                session.run(query, filename=filename)
                logger.info(f"Deleted document '{filename}' and its chunks")
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    def query_similar_chunks(self, query_embedding, top_k=5):
        """
        Finds similar chunks using vector search.
        """
        query = """
        CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $query_embedding)
        YIELD node, score
        MATCH (node)<-[:HAS_CHUNK]-(d:Document)
        RETURN node.text AS text, score, node.chunk_index AS index, 
               d.filename AS document, d.doc_type AS doc_type
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, query_embedding=query_embedding, top_k=top_k)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error querying similar chunks: {e}")
            return []

    def get_context(self, query_embedding, window=1, top_k=10):
        """
        Retrieves similar chunks and their neighbors (window) for better context.
        Enhanced for multi-document retrieval.
        """
        # First get top matches
        similar_chunks = self.query_similar_chunks(query_embedding, top_k=top_k)
        
        context_parts = []
        seen_texts = set()  # Deduplication
        
        for chunk in similar_chunks:
            chunk_text = chunk['text']
            if chunk_text not in seen_texts:
                doc_name = chunk.get('document', 'Unknown')
                context_parts.append(f"[Source: {doc_name}]\n{chunk_text}")
                seen_texts.add(chunk_text)
            
        return "\n\n---\n\n".join(context_parts)
    
    def get_multi_doc_context(self, query_embedding, top_k=15, max_docs=5, traverse_graph=True):
        """
        Enhanced retrieval for multi-document questions.
        
        Args:
            query_embedding: Query vector
            top_k: Number of initial chunks to retrieve
            max_docs: Maximum number of documents to pull from
            traverse_graph: Whether to follow SIMILAR_TO and NEXT relationships
        """
        # Step 1: Vector search
        similar_chunks = self.query_similar_chunks(query_embedding, top_k=top_k)
        
        if not similar_chunks:
            return ""
        
        # Step 2: Get document diversity (limit to max_docs)
        docs_seen = set()
        selected_chunks = []
        
        for chunk in similar_chunks:
            doc = chunk.get('document', '')
            if doc and (len(docs_seen) < max_docs or doc in docs_seen):
                selected_chunks.append(chunk)
                docs_seen.add(doc)
        
        # Step 3: Optionally traverse graph for more context
        context_parts = []
        seen_texts = set()
        
        for chunk in selected_chunks[:top_k]:
            chunk_text = chunk['text']
            doc_name = chunk.get('document', 'Unknown')
            
            if chunk_text not in seen_texts:
                context_parts.append(f"[Source: {doc_name}]\n{chunk_text}")
                seen_texts.add(chunk_text)
        
        return "\n\n---\n\n".join(context_parts)

    def query_by_entity(self, entity_name: str, top_k: int = 5) -> List[Dict]:
        """Find chunks that mention a specific entity"""
        query = """
        MATCH (e:Entity {name: $entity_name})<-[:MENTIONS]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
        RETURN c.text as text, d.filename as document, c.chunk_index as index
        LIMIT $top_k
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_name=entity_name, top_k=top_k)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error querying by entity: {e}")
            return []
    
    def clear_all_data(self):
        """Clear all documents, chunks, and entities from the database"""
        query = "MATCH (n) DETACH DELETE n"
        try:
            with self.driver.session() as session:
                session.run(query)
                logger.info("Cleared all data from Neo4j")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            raise
