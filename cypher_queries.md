# Neo4j Cypher Query Reference

Essential Cypher queries for exploring and debugging your multi-document knowledge graph.

## Basic Queries

### 1. View All Documents
```cypher
MATCH (d:Document)
RETURN d.filename, d.doc_type, d.upload_date, d.chunk_count
ORDER BY d.upload_date DESC
```

### 2. Count Nodes by Type
```cypher
MATCH (n)
RETURN labels(n) as type, count(n) as count
ORDER BY count DESC
```

### 3. View First Few Chunks of a Document
```cypher
MATCH (d:Document {filename: "alzheimer_clinical_trial_protocol.pdf"})-[:HAS_CHUNK]->(c:Chunk)
RETURN c.chunk_index, substring(c.text, 0, 100) + "..." as preview
ORDER BY c.chunk_index
LIMIT 5
```

### 4. Database Statistics
```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
RETURN 
  count(DISTINCT d) as documents,
  count(DISTINCT c) as chunks,
  count(DISTINCT e) as entities
```

---

## Entity Queries

### 5. Find All Entities by Type
```cypher
MATCH (e:Entity)
RETURN e.type, count(e) as count
ORDER BY count DESC
```

### 6. Top 20 Most Mentioned Entities
```cypher
MATCH (e:Entity)
RETURN e.name, e.type, e.mentions_count
ORDER BY e.mentions_count DESC
LIMIT 20
```

### 7. Find All Documents Mentioning a Specific Entity
```cypher
MATCH (e:Entity {name: "NeuroX-2024"})<-[:MENTIONS]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
RETURN DISTINCT d.filename, count(c) as mentions
ORDER BY mentions DESC
```

### 8. Find Chunks Mentioning Multiple Specific Entities
```cypher
MATCH (c:Chunk)-[:MENTIONS]->(e:Entity)
WHERE e.name IN ["NeuroX-2024", "ARIA-E", "CDR-SB"]
WITH c, collect(DISTINCT e.name) as entities
WHERE size(entities) >= 2
MATCH (c)<-[:HAS_CHUNK]-(d:Document)
RETURN d.filename, c.chunk_index, entities, 
       substring(c.text, 0, 150) + "..." as preview
ORDER BY size(entities) DESC, d.filename, c.chunk_index
```

### 9. Find Drugs and Their Associated Diseases
```cypher
MATCH (drug:Entity {type: "drug"})<-[:MENTIONS]-(c:Chunk)-[:MENTIONS]->(disease:Entity {type: "disease"})
RETURN DISTINCT drug.name, collect(DISTINCT disease.name) as diseases
ORDER BY drug.name
```

---

## Cross-Document Relationship Queries

### 10. Find Cross-Document Similar Chunks
```cypher
MATCH (c1:Chunk)-[s:SIMILAR_TO]->(c2:Chunk)
WHERE (c1)<-[:HAS_CHUNK]-(:Document) AND (c2)<-[:HAS_CHUNK]-(:Document)
RETURN c1, s, c2
LIMIT 25
```

### 11. Find Similar Chunks Between Two Specific Documents
```cypher
MATCH (d1:Document {filename: "alzheimer_clinical_trial_protocol.pdf"})-[:HAS_CHUNK]->(c1:Chunk)
MATCH (d2:Document {filename: "alzheimer_clinical_trial_results.pdf"})-[:HAS_CHUNK]->(c2:Chunk)
MATCH (c1)-[s:SIMILAR_TO]-(c2)
RETURN 
  c1.chunk_index as protocol_chunk,
  c2.chunk_index as results_chunk,
  s.score as similarity,
  substring(c1.text, 0, 100) as protocol_preview,
  substring(c2.text, 0, 100) as results_preview
ORDER BY s.score DESC
LIMIT 10
```

### 12. Document Co-Occurrence Network (Shared Entities)
```cypher
MATCH (d1:Document)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(:Chunk)<-[:HAS_CHUNK]-(d2:Document)
WHERE id(d1) < id(d2)
WITH d1, d2, collect(DISTINCT e.name) as shared_entities
WHERE size(shared_entities) >= 3
RETURN d1.filename, d2.filename, shared_entities, size(shared_entities) as overlap
ORDER BY overlap DESC
LIMIT 20
```

### 13. Count Cross-Document Links by Document Pair
```cypher
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)-[s:SIMILAR_TO]-(c2:Chunk)<-[:HAS_CHUNK]-(d2:Document)
WHERE d1.filename < d2.filename
RETURN d1.filename, d2.filename, count(s) as links, avg(s.score) as avg_similarity
ORDER BY links DESC
```

---

## Vector Search Simulation

### 14. Find Chunks Similar to a Sample Text (Manual)
First, get embeddings for a query in Python, then:
```cypher
// Replace $query_embedding with actual embedding vector
CALL db.index.vector.queryNodes('chunk_embeddings', 10, $query_embedding)
YIELD node, score
MATCH (node)<-[:HAS_CHUNK]-(d:Document)
RETURN d.filename, node.chunk_index, score, 
       substring(node.text, 0, 200) as preview
ORDER BY score DESC
```

### 15. Chunks with Highest Embedding Variance (Outliers)
```cypher
// This is conceptual - actual implementation would need custom procedure
MATCH (c:Chunk)
WHERE c.embedding IS NOT NULL
RETURN c, size(c.embedding) as dimensions
LIMIT 10
```

---

## Sequential Context Queries

### 16. Get Chunk with Surrounding Context (Previous & Next)
```cypher
MATCH (c:Chunk {chunk_index: 5})<-[:HAS_CHUNK]-(d:Document {filename: "alzheimer_clinical_trial_results.pdf"})
OPTIONAL MATCH (prev:Chunk)-[:NEXT]->(c)
OPTIONAL MATCH (c)-[:NEXT]->(next:Chunk)
RETURN 
  prev.text as previous_chunk,
  c.text as current_chunk,
  next.text as next_chunk
```

### 17. Get Extended Window (5 chunks around target)
```cypher
MATCH path = (start:Chunk)-[:NEXT*0..2]->(c:Chunk {chunk_index: 10})-[:NEXT*0..2]->(end:Chunk)
WHERE (start)<-[:HAS_CHUNK]-(:Document {filename: "alzheimer_drug_mechanism.pdf"})
RETURN [node IN nodes(path) | substring(node.text, 0, 80)] as context_window
LIMIT 1
```

---

## Data Quality & Debugging

### 18. Find Documents Without Cross-Doc Links
```cypher
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->(:Chunk)-[:SIMILAR_TO]-(:Chunk)
RETURN d.filename, d.doc_type
```

### 19. Find Chunks Without Entity Mentions
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE NOT (c)-[:MENTIONS]->(:Entity)
RETURN d.filename, count(c) as chunks_without_entities
ORDER BY chunks_without_entities DESC
```

### 20. Check Vector Index Status
```cypher
SHOW INDEXES
YIELD name, type, entityType, properties, state
WHERE name = 'chunk_embeddings'
RETURN *
```

### 21. Validate Embedding Dimensions
```cypher
MATCH (c:Chunk)
WHERE c.embedding IS NOT NULL
RETURN size(c.embedding) as dimensions, count(c) as count
```

---

## Visualization Queries

### 22. Visualize a Document's Entity Network
```cypher
MATCH (d:Document {filename: "alzheimer_clinical_trial_protocol.pdf"})-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(e:Entity)
RETURN d, c, e
LIMIT 50
```

### 23. Visualize Cross-Document Knowledge Graph
```cypher
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)-[s:SIMILAR_TO]-(c2:Chunk)<-[:HAS_CHUNK]-(d2:Document)
WHERE s.score > 0.8
RETURN d1, c1, s, c2, d2
LIMIT 30
```

### 24. Entity Co-Mention Network
```cypher
MATCH (e1:Entity)<-[:MENTIONS]-(c:Chunk)-[:MENTIONS]->(e2:Entity)
WHERE e1.name < e2.name AND e1.type IN ['drug', 'disease'] AND e2.type IN ['drug', 'disease']
WITH e1, e2, count(c) as co_mentions
WHERE co_mentions >= 2
RETURN e1, e2, co_mentions
ORDER BY co_mentions DESC
LIMIT 25
```

---

## Maintenance & Cleanup

### 25. Delete a Specific Document and All Related Nodes
```cypher
MATCH (d:Document {filename: "test_document.pdf"})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
OPTIONAL MATCH (c)-[r]-()
DELETE r, c, d
```

### 26. Delete All SIMILAR_TO Relationships (Useful Before Re-Creating)
```cypher
MATCH ()-[s:SIMILAR_TO]-()
DELETE s
```

### 27. Delete Orphaned Entity Nodes (No Incoming MENTIONS)
```cypher
MATCH (e:Entity)
WHERE NOT (e)<-[:MENTIONS]-()
DELETE e
```

### 28. Clear Entire Database (⚠️ DESTRUCTIVE)
```cypher
MATCH (n)
DETACH DELETE n
```

---

## Performance Queries

### 29. Find Longest Chunks
```cypher
MATCH (c:Chunk)
RETURN c.text, length(c.text) as text_length, c.chunk_index
ORDER BY text_length DESC
LIMIT 10
```

### 30. Find Documents with Most Chunks
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d.filename, count(c) as chunk_count
ORDER BY chunk_count DESC
```

---

## Advanced Analytics

### 31. Entity Type Distribution Across Documents
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(e:Entity)
RETURN d.filename, e.type, count(DISTINCT e) as unique_entities
ORDER BY d.filename, unique_entities DESC
```

### 32. Find "Bridge" Chunks (Connect Multiple Documents via Similarity)
```cypher
MATCH (c:Chunk)-[s:SIMILAR_TO]-()
WITH c, count(s) as link_count
WHERE link_count >= 3
MATCH (c)<-[:HAS_CHUNK]-(d:Document)
RETURN d.filename, c.chunk_index, link_count, 
       substring(c.text, 0, 150) as preview
ORDER BY link_count DESC
LIMIT 10
```

### 33. Calculate Graph Density
```cypher
MATCH (c:Chunk)
WITH count(c) as node_count
MATCH ()-[s:SIMILAR_TO]-()
WITH node_count, count(s) as edge_count
RETURN node_count, edge_count, 
       toFloat(edge_count) / (node_count * (node_count - 1)) as density
```

---

## Integration with Python

### 34. Export Document Metadata for Analysis
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(e:Entity)
RETURN d.filename, d.doc_type, 
       count(DISTINCT c) as chunks,
       count(DISTINCT e) as entities,
       collect(DISTINCT e.type) as entity_types
```

Use this in Python with:
```python
from utils.neo4j_manager import Neo4jManager

neo = Neo4jManager()
with neo.driver.session() as session:
    result = session.run(query)
    data = [record.data() for record in result]
neo.close()
```

---

**Tip:** Run queries in the Neo4j Browser ([http://localhost:7474](http://localhost:7474)) for interactive visualization!
