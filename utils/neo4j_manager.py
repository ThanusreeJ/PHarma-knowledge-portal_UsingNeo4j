import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

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
        # Check if index exists first to avoid potential hangs with 'IF NOT EXISTS'
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

    def add_document(self, filename, chunks, embeddings):
        """
        Adds a document and its chunks to the graph.
        
        Args:
            filename (str): Name of the file.
            chunks (list of str): Text content of chunks.
            embeddings (list of list of floats): Embeddings for each chunk.
        """
        query = """
        MERGE (d:Document {filename: $filename})
        ON CREATE SET d.upload_date = datetime()
        WITH d
        UNWIND range(0, size($chunks)-1) AS i
        CREATE (c:Chunk {
            text: $chunks[i],
            embedding: $embeddings[i],
            chunk_index: i
        })
        MERGE (d)-[:HAS_CHUNK]->(c)
        WITH c, i
        ORDER BY i
        WITH collect(c) as chunk_nodes
        FOREACH (j in range(0, size(chunk_nodes)-2) |
            FOREACH (c1 in [chunk_nodes[j]] |
                FOREACH (c2 in [chunk_nodes[j+1]] |
                    MERGE (c1)-[:NEXT]->(c2)
                )
            )
        )
        """
        try:
            with self.driver.session() as session:
                session.run(query, filename=filename, chunks=chunks, embeddings=embeddings)
            logger.info(f"Document '{filename}' added with {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise

    def query_similar_chunks(self, query_embedding, top_k=5):
        """
        Finds similar chunks using vector search.
        """
        query = """
        CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $query_embedding)
        YIELD node, score
        RETURN node.text AS text, score, node.chunk_index AS index
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, query_embedding=query_embedding, top_k=top_k)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error querying similar chunks: {e}")
            return []

    def get_context(self, query_embedding, window=1):
        """
        Retrieves similar chunks and their neighbors (window) for better context.
        """
        # First get top matches
        similar_chunks = self.query_similar_chunks(query_embedding)
        
        context_texts = []
        for chunk in similar_chunks:
            # For each chunk, you might want to get previous/next chunks
            # For simplicity in this PoC, we'll just return the matched text
            # Enhancing this to use [:NEXT] relationships is a good next step
            context_texts.append(chunk['text'])
            
        return "\n\n".join(context_texts)
