# Neo4j & Podman Integration for RAG

This document outlines how to set up Neo4j using Podman, integrate it with the Pharma Knowledge Portal for RAG (Retrieval-Augmented Generation), and verify the setup.

## 1. Prerequisites

- **Podman**: Installed and running on your machine.
- **Python 3.10+**: The project environment.
- **Groq API Key**: For embedding generation and chat (ensure it's in `.env`).

## 2. Setting up Neo4j with Podman

### Pull and Run Neo4j

We will use the official Neo4j image. This command pulls the image and runs it, exposing the necessary ports (7474 for HTTP, 7687 for Bolt).

```bash
# Pull the latest Neo4j image
podman pull docker.io/neo4j:latest

# Run Neo4j Container
# Replace 'password' with a strong password of your choice
podman run -d \
    --name neo4j-pharma \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    docker.io/neo4j:latest
```

### Verification (Podman)

Check if the container is running:

```bash
podman ps
```

You should see `neo4j-pharma` in the list with status `Up`.

### Verification (Browser)

1.  Open your browser and navigate to [http://localhost:7474](http://localhost:7474).
2.  Connect using:
    -   **Connect URL**: `bolt://localhost:7687`
    -   **Username**: `neo4j`
    -   **Password**: `password` (or whatever you set in the command above)

If you can see the Neo4j Browser dashboard, the database is ready.

## 3. RAG Architecture with Neo4j

In this Proof of Concept (PoC), Neo4j acts as a **Graph Vector Store**.

1.  **Ingestion**: 
    -   PDF Documents (e.g., Clinical Trial Reports, Research Papers) are parsed.
    -   Text is split into chunks.
    -   Embeddings are generated for each chunk using `sentence-transformers` or Groq.
    -   **Nodes**: `Document` (metadata), `Chunk` (text content + embedding).
    -   **Relationships**: `(Document)-[:HAS_CHUNK]->(Chunk)`, `(Chunk)-[:NEXT]->(Chunk)`.
2.  **Retrieval**:
    -   User query is embedded.
    -   A Vector Search (or hybrid search) identifies relevant `Chunk` nodes.
    -   The graph structure allows retrieving surrounding context (previous/next chunks) for better answer quality.
3.  **Generation**:
    -   Retrieved context is sent to the LLM (Groq) to generate the answer.

## 4. Required Dependencies

Add the following to your `requirements.txt`:

```text
neo4j>=5.18.0
```

And ensure you have:
```text
sentence-transformers>=2.3.1
langchain-community>=0.0.10
```

## 5. Implementation Details

### Nodes and Relationships

-   **Node: Document**
    -   Properties: `filename`, `upload_date`, `type` (e.g., 'clinical_trial', 'research_paper')
-   **Node: Chunk**
    -   Properties: `text`, `embedding`, `page_number`, `chunk_index`
-   **Relationship: HAS_CHUNK**
    -   `(:Document)-[:HAS_CHUNK]->(:Chunk)`
-   **Relationship: NEXT**
    -   `(:Chunk)-[:NEXT]->(:Chunk)` (Linking sequential text chunks)

### Example Cypher Queries for Testing

**1. View Setup/Nodes:**
```cypher
MATCH (n) RETURN n LIMIT 25
```

**2. Check Documents:**
```cypher
MATCH (d:Document) RETURN d.filename, d.upload_date
```

**3. Vector Search (Conceptual):**
*(Note: Actual vector search requires an index. We will create a `vector` index on `Chunk` nodes)*

```cypher
// Create Vector Index (Run this once via Python or Browser)
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 384,
 `vector.similarity_function`: 'cosine'
}}
```

**4. Simple Keyword Search:**
```cypher
MATCH (c:Chunk) 
WHERE c.text CONTAINS 'side effects'
RETURN c.text, c.page_number
LIMIT 5
```

## 6. End-to-End Testing Guide

### Step 1: Prepare Test Documents
You need a sample PDF file.
-   **Type**: Clinical Trial Results or Drug Leaflet.
-   **Size**: Small (1-5 pages) for quick testing.
-   **Content**: Clear text (not scanned images without OCR).

### Step 2: Configure Environment
In your `.env` file, add:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Step 3: Run the Application
```bash
streamlit run app.py
```

### Step 4: Ingestion Test
1.  Go to the **Chatbot** tab.
2.  Look for the "RAG / Document Upload" sidebar section.
3.  Upload your test PDF.
4.  Wait for the success message "Document processed and graph created!".

### Step 5: Verification
1.  Open Neo4j Browser.
2.  Run `MATCH (n:Chunk) RETURN count(n)`. Count should be > 0.

### Step 6: Retrieval Test
1.  In the Chatbot, ask a specific question found in the PDF.
2.  Verify the answer references the document content.

## 7. Troubleshooting

**Neo4j Connection Failed:**
-   Ensure Podman container is running (`podman ps`).
-   Check ports `7474` and `7687` are not blocked.
-   Verify `.env` credentials match the `podman run` command.

**Embeddings/Import Errors:**
-   Ensure `sentence-transformers` is installed.
-   If you get PyTorch errors, try reinstalling `torch` compatible with your OS.

**Empty Responses:**
-   Ensure the PDF has extractable text (try copy-pasting text from PDF to Notepad to verify).
-   Check if Groq API key is valid.

**Podman Issues:**
-   If `podman` command is not found, ensure it is in your system PATH.
-   If permission denied, try running terminal as Administrator.

## 8. Understanding the Graph Visualization

When you run `MATCH (n) RETURN n` in the Neo4j Browser, you see a visual representation of your data. This is a great way to show the "brain" of your application.

### What do the shapes mean?
-   **Orange Node (Document)**: This represents the **File** you uploaded. It acts as the "parent" container.
-   **Purple Nodes (Chunk)**: These are the **Parts** of the document. The system splits the PDF into smaller pieces (chunks) so the AI can process them easily.

### What do the arrows mean?
-   **`HAS_CHUNK`**: Connects the **Document** to its **Parts**. It shows "This file contains these text blocks."
-   **`NEXT`**: Connects one **Chunk** to the next. This preserves the **reading order**, allowing the AI to understand flow and context.

## 9. Test Questions for `sample_clinical_trial.pdf`

If you uploaded the generated sample PDF, here are some questions to test the RAG capabilities:

### Simple Fact Retrieval
1.  **"What is the primary condition treated by NeuroX-2024?"**
    -   *Expected Answer:* Alzheimer's Disease.
2.  **"How many participants were in the Phase 3 trial?"**
    -   *Expected Answer:* 2,500 participants.
3.  **"What were the common side effects?"**
    -   *Expected Answer:* Infusion-related reactions (12%) and ARIA-E (15%).

### Complex Synthesis
1.  **"Did the drug meet its primary endpoint? Explain with statistics."**
    -   *Expected Answer:* Yes, it slowed cognitive decline by 27% on the CDR-SB scale (p=0.001).
2.  **"What is the next regulatory step for NeuroX-2024?"**
    -   *Expected Answer:* FDA submission is planned for Q4 2024.
3.  **"Summarize the safety and efficacy results."**
3.  **"Summarize the safety and efficacy results."**
    -   *Expected Answer:* The drug is effective in slowing decline and reducing amyloid, with a manageable safety profile (mainly infusion reactions and ARIA-E).

## 10. Conceptual Explanation: Why Neo4j?

If you are wondering **"Why is this better than just searching a PDF?"**, here is a simple analogy.

### The "Rip and Pile" vs. "The Book"

**Traditional Search (No Graph)**
Imagine tearing every page out of a textbook and throwing them into a pile.
-   If you ask *"What is the side effect?"*, you might find a page that says *"Nausea"*.
-   **The Problem:** You lost the context. You don't know *which* drug caused it, or if it was a mild or severe side effect mentioned on the **previous page**.

**Graph RAG (Neo4j)**
Neo4j keeps the pages **bound together** (using the `NEXT` arrows you saw).
-   **Vector Search** acts like a **Magnet**: It pulls you to the *right page* based on your question.
-   **Graph Traversal** acts like **Reading**: Once you land on that page, the graph lets the AI "look left" (previous page) and "look right" (next page) to understand the **Full Context**.

### Why "Complex" Questions need the Graph
-   **Simple Question**: "What is the dose?" -> reliable answer on Page 5.
-   **Complex Question**: "Did the drug meet its goals?"
    -   Page 2 might say: *"The goal is to lower amyloid."*
    -   Page 10 might say: *"Amyloid levels dropped by 80%."*
    -   The Graph (and the AI) connects these two pieces of information to give you the answer: *"Yes, because Page 10 confirms the goal set on Page 2."*

## 11. Advanced Stress Testing (for `complex_clinical_protocol.pdf`)

Use these questions to prove that your Neo4j RAG is working better than a simple search.

### 1. The "Cross-Reference" Challenge
*   **Question:** "The introduction mentions replicating a primary outcome. What is the specific metric and timeframe for this primary endpoint?"
*   **Expected Answer:** "Change from baseline in CDR-SB score at Week 72." (The intro mentions the goal, but Section 4.1 defines the specific metric).

### 2. The "Conditional Logic" Challenge
*   **Question:** "A patient shows asymptomatic moderate ARIA-E. What should the investigator do?"
*   **Expected Answer:** "Suspend dosing until resolution." (Found in Section 5.1).

### 3. The "Synthesis" Challenge
*   **Question:** "List all the secondary objectives and their corresponding endpoints."
*   **Expected Answer:**
    -   *Objectives:* Assess safety/tolerability, measure amyloid reduction, evaluate tau biomarkers.
    -   *Endpoints:* Change in ADAS-Cog13 and ADCS-ADL-MCI scores at Week 72.

### 4. The "Specific Detail" Challenge
*   **Question:** "What is the temperature range for drug storage?"
*   **Expected Answer:** "Between 2 and 8 degrees Celsius." (Buried in the Operational Details section).

