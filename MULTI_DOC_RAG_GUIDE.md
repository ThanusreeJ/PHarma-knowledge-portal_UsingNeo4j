# Multi-Document Neo4j RAG Guide

## Overview

The Pharma Knowledge Portal now supports **multi-document Retrieval-Augmented Generation (RAG)** powered by Neo4j graph database. This enables you to upload multiple pharmaceutical documents and ask complex questions that require synthesizing information across all of them.

## Key Features

### 🔗 Graph-Based Knowledge Representation
- **Documents** and **Chunks** (text segments) stored as nodes
- **Entities** (drugs, diseases, proteins, companies) automatically extracted and linked
- **Cross-document relationships** automatically created between similar content
- **Sequential relationships** preserve document flow and context

### 📚 Multi-Document Upload
- Upload multiple PDFs simultaneously or incrementally
- Automatic document type detection (clinical trial, research paper, drug label, etc.)
- Document management: view, delete specific docs, or clear all

### 🧠 Intelligent Retrieval
- Vector search across all documents
- Graph traversal to find related information
- Entity-based expansion for comprehensive answers
- Source citation showing which documents contributed to the answer

---

## Getting Started

### 1. Upload Documents

**Go to: Company Knowledge tab**

1. Click "Browse files" or drag & drop PDF documents
2. Select one or more PDFs (you can upload up to 10 at once)
3. Click "📥 Process Documents"
4. Wait 30-90 seconds for processing (you'll see a progress indicator)

**What happens during processing:**
- PDF text extraction
- Text chunking (1000 chars with 200 char overlap)
- Embedding generation (384-dimensional vectors)
- Entity extraction (drugs, diseases, proteins, trial IDs, companies)
- Graph creation in Neo4j
- Cross-document similarity link creation

### 2. View Your Knowledge Base

In the **sidebar**, you'll see:
- Total document count
- List of all uploaded documents with:
  - Filename
  - Document type (auto-detected)
  - Upload date
  - Number of text chunks

### 3. Ask Questions

You can ask questions in either:
- **Company Knowledge tab** - Dedicated RAG interface
- **Chatbot tab** - General chatbot that automatically uses RAG when documents are loaded

**Example questions:**
- "What was the primary endpoint and did the trial meet it?" (needs Protocol + Results)
- "Explain the mechanism behind ARIA-E and its incidence in the trial" (needs Mechanism + Results)
- "Compare the protocol design to the actual results"

---

## Test Documents

Three interrelated test documents are provided in the `test_documents/` folder:

### 1. alzheimer_clinical_trial_protocol.pdf
**Content:**
- Phase 3 trial design for NeuroX-2024
- Primary endpoint: CDR-SB at Week 72
- Target: 25% slowing of cognitive decline
- ARIA-E monitoring protocol
- 2,500 participants, 72 weeks

### 2. alzheimer_clinical_trial_results.pdf
**Content:**
- Trial results for NCT04567891
- Primary endpoint: **27% slowing achieved** (met target!)
- CDR-SB difference: -0.45 points (p=0.001)
- ARIA-E incidence: 15% in treatment group
- 82% amyloid reduction

### 3. alzheimer_drug_mechanism.pdf
**Content:**
- Mechanism of action for anti-amyloid antibodies
- Explanation of CDR-SB and ADAS-Cog13 scales
- ARIA-E pathophysiology
- Biomarker interpretation (amyloid PET, p-tau217)

---

## Test Questions

Upload all three PDFs and try these questions to validate multi-document synthesis:

### Simple (Single Document)
1. "How many participants were in the Phase 3 trial?" → Protocol
2. "What was the primary endpoint result?" → Results
3. "What is the mechanism of anti-amyloid antibodies?" → Mechanism

### Complex (Multi-Document)
1. **Cross-Reference:** "What was the primary endpoint for NeuroX-2024 and did it meet that endpoint?"
   - *Expected:* CDR-SB at Week 72 (Protocol) + 27% slowing vs. 25% target (Results) = Yes, it met it

2. **Synthesis:** "Explain the mechanism behind the cognitive improvements seen in the trial"
   - *Expected:* Anti-amyloid mechanism (Mechanism) + amyloid reduction data (Results) + cognitive outcomes (Results)

3. **Safety Integration:** "What is ARIA-E and how frequently was it observed in the trial?"
   - *Expected:* Pathophysiology explanation (Mechanism) + protocol monitoring (Protocol) + incidence data (Results)

4. **Comparison:** "Did the trial meet the protocol-defined success criteria?"
   - *Expected:* Protocol target 25% (Protocol) vs. achieved 27% (Results) = Yes

---

## Understanding the Graph Structure

### Nodes

1. **Document**
   - `filename`: PDF filename
   - `upload_date`: Timestamp
   - `doc_type`: clinical_trial_protocol, clinical_trial_results, drug_mechanism, research_paper, etc.
   - `file_hash`: For deduplication

2. **Chunk**
   - `text`: Actual content (1000 chars)
   - `embedding`: 384-dim vector
   - `chunk_index`: Order in document (0, 1, 2...)

3. **Entity**
   - `name`: Entity name (e.g., "NeuroX-2024", "ARIA-E", "Alzheimer's")
   - `type`: drug, disease, protein, company, clinical_trial_id, gene
   - `mentions_count`: How many chunks mention this entity

### Relationships

1. **HAS_CHUNK**: `(Document)-[:HAS_CHUNK]->(Chunk)`
   - Links document to its content chunks

2. **NEXT**: `(Chunk)-[:NEXT]->(Chunk)`
   - Sequential flow within a document
   - Preserves reading order for context

3. **MENTIONS**: `(Chunk)-[:MENTIONS]->(Entity)`
   - Chunk contains this entity
   - Enables entity-based retrieval

4. **SIMILAR_TO**: `(Chunk)-[:SIMILAR_TO {score: float}]->(Chunk)`
   - Cross-document similarity (score > 0.75)
   - Created between chunks from different documents
   - Enables finding related content across documents

---

## Document Management

### View All Documents
Sidebar in Company Knowledge tab shows all uploaded documents

### Delete a Document
1. Expand the document in the sidebar
2. Click "🗑️ Delete"
3. Confirmation and reload

### Clear All Documents
1. Click "🗑️ Clear All Documents" in sidebar
2. Click again to confirm
3. **Warning:** This deletes ALL data from Neo4j!

---

## Neo4j Browser Exploration

Open [http://localhost:7474](http://localhost:7474) to visualize your knowledge graph.

### Useful Cypher Queries

See `cypher_queries.md` for comprehensive examples.

**Quick Start:**
```cypher
// View all documents
MATCH (d:Document) RETURN d

// Count chunks per document
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d.filename, count(c) as chunks
ORDER BY chunks DESC

// Find top entities
MATCH (e:Entity)
RETURN e.name, e.type, e.mentions_count
ORDER BY e.mentions_count DESC
LIMIT 10

// Visualize cross-document links
MATCH (c1:Chunk)-[s:SIMILAR_TO]->(c2:Chunk)
WHERE s.score > 0.8
RETURN c1, s, c2
LIMIT 25
```

---

## Troubleshooting

### Documents not processing
- **Check:** PDF has extractable text (not scanned image)
- **Check:** Neo4j is running (`podman ps` should show neo4j-pharma)
- **Check:** File size < 50MB (large files take longer)

### No cross-document relationships created
- **Reason:** Need at least 2 documents with similar content
- **Reason:** Similarity threshold is 0.75 (very high)
- **Solution:** Upload related documents (e.g., protocol + results)

### Answers not referencing all documents
- **Check:** Question actually requires multiple documents
- **Adjust:** Increase `top_k` parameter in retrieval (default: 15)
- **Check:** Documents contain overlapping entities/topics

### scispacy errors
- **Install biomedical model:**
  ```bash
  pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz
  ```

### Neo4j connection issues
- **Check:** Container running: `podman ps`
- **Restart:** `podman start neo4j-pharma`
- **Check credentials:** `.env` file has correct NEO4J_PASSWORD

---

## Advanced: How It Works

### Ingestion Pipeline
1. **Parse PDF** → Extract text
2. **Detect Type** → Classify document (protocol, results, etc.)
3. **Chunk** → Split into 1000-char segments with 200-char overlap
4. **Embed** → Generate vectors using sentence-transformers
5. **Extract Entities** → Use scispacy + pattern matching
6. **Store in Neo4j** → Create Document, Chunk, Entity nodes
7. **Create Links** → HAS_CHUNK, NEXT, MENTIONS relationships
8. **Cross-Link** → Compute chunk similarities across documents (SIMILAR_TO)

### Retrieval Strategy
1. **Vector Search** → Find top-k similar chunks across all documents
2. **Document Diversity** → Ensure results from multiple sources (up to max_docs)
3. **Graph Traversal** → Optional expansion via NEXT and SIMILAR_TO
4. **Deduplicate** → Remove redundant content
5. **Format** → Add source citations `[Source: filename]`
6. **Send to LLM** → Generate answer with context

### Why Neo4j vs FAISS?
| Feature | FAISS | Neo4j |
|---------|-------|-------|
| Vector search | ✅ Very fast | ✅ Fast enough |
| Relationships | ❌ None | ✅ Rich graph |
| Entity linking | ❌ Manual | ✅ Automatic |
| Cross-doc links | ❌ Not possible | ✅ Native support |
| Explainability | ❌ Black box | ✅ Visualizable graph |

---

## Best Practices

1. **Upload related documents** - Protocol + Results works better than random papers
2. **Descriptive filenames** - Use clear names like "trial_protocol.pdf" not "doc1.pdf"
3. **Check document library** - Verify all uploads succeeded before querying
4. **Start with simple questions** - Test single-doc retrieval before complex multi-doc
5. **Use entity names** - Mention specific drugs/diseases for better retrieval
6. **Monitor Neo4j** - Check graph in browser to understand your knowledge base

---

## Performance Notes

- **Upload time:** 30-60 sec per document (includes entity extraction + cross-linking)
- **Query time:** 2-5 seconds (vector search + graph traversal + LLM)
- **Storage:** ~5-10 MB per 100-page document in Neo4j
- **RAM:** Embedding model uses ~500 MB, scispacy ~300 MB

---

**Questions or issues?** Check the `cypher_queries.md` for debugging queries or review the implementation in `utils/neo4j_manager.py`.
