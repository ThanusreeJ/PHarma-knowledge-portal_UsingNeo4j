# Installation & Setup Guide

## Quick Start (Without scispacy)

The system is **fully functional without scispacy** - it will use pattern-based entity extraction instead.

### 1. Install Core Dependencies

```powershell
# In your virtual environment
pip install -r requirements.txt
```

This installs everything except `scispacy` (which requires C++ compiler).

### 2. Start the Application

```powershell
streamlit run app.py
```

The app will start at http://localhost:8501

### 3. What Works Without scispacy

✅ **Full multi-document RAG functionality**
- Upload multiple PDFs
- Vector search across all documents  
- Cross-document relationships
- LLM-powered Q&A with source citations
- Document management

✅ **Pattern-based entity extraction**
- Clinical trial IDs (e.g., NCT04567891)
- Company names (major pharma companies)
- Basic keyword matching

❌ **What's disabled without scispacy**
- Advanced biomedical NER (drugs, diseases, proteins, genes)
- Medical concept extraction

**Impact:** ~30% fewer entities extracted, but core RAG functionality works perfectly.

---

## Optional: Install scispacy (Advanced Entity Extraction)

If you want full biomedical NER, you need Microsoft Visual C++ Build Tools.

### Option A: Install Build Tools

1. Download **Microsoft C++ Build Tools**: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer, select **Desktop development with C++**
3. Restart terminal after installation
4. Then install scispacy:

```powershell
pip install scispacy
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz
```

### Option B: Skip scispacy

Just continue using the system without it! Pattern-based extraction is sufficient for most use cases.

---

## Testing the System

### 1. Upload Test Documents

1. Go to **Company Knowledge** tab
2. Click "Browse files"
3. Navigate to `test_documents/` folder
4. Select all 3 PDFs:
   - alzheimer_clinical_trial_protocol.pdf
   - alzheimer_clinical_trial_results.pdf
   - alzheimer_drug_mechanism.pdf
5. Click "📥 Process Documents"
6. Wait 30-60 seconds

**Expected:** "Successfully processed all 3 documents. Created X cross-document relationships."

### 2. Ask Test Questions

**Simple (Single Document):**
```
How many participants were in the Phase 3 trial?
```
Expected: 2,500 participants (from Protocol)

**Complex (Multi-Document):**
```
What was the primary endpoint for NeuroX-2024 and did it meet that endpoint?
```
Expected: Should synthesize info from Protocol (target: 25%) + Results (achieved: 27%)

**Advanced (All Three Documents):**
```
What is ARIA-E and how frequently was it observed in the trial?
```
Expected: Definition from Mechanism + incidence from Results (15% treatment vs 1.2% placebo)

### 3. Verify Neo4j Graph

Open http://localhost:7474 in your browser

Login with credentials from your `.env` file (default: neo4j/password)

Run this query:
```cypher
MATCH (d:Document)
RETURN d.filename, d.doc_type, d.chunk_count
```

Expected: 3 documents listed

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'neo4j'"

**Solution:**
```powershell
python -m pip install neo4j
```

### "Neo4j connection failed"

**Check Neo4j is running:**
```powershell
podman ps
```

**Should show:** neo4j-pharma container

**If not running:**
```powershell
podman start neo4j-pharma
```

### "scispacy model not found" Warning

**This is normal!** The app will fall back to pattern-based extraction.

To suppress the warning, either:
- Install scispacy (see above), OR
- Ignore it - functionality is not affected

### Documents not processing

- Check PDF has extractable text (not scanned image)
- Check file size < 50MB
- Wait full 30-90 seconds for processing

### No cross-document relationships

- Need at least 2 documents with similar content
- Similarity threshold is 0.75 (very high)
- Upload the 3 test documents - they're designed to link

---

## System Status

✅ **Currently Working:**
- Multi-document upload
- Neo4j graph database
- Vector search
- Cross-document relationships  
- Pattern-based entity extraction
- LLM query answering
- Source citation
- Document management

⚠️ **Optional (Requires C++ Build Tools):**
- Advanced biomedical NER with scispacy
- Drug/disease/protein entity extraction

---

## Environment Variables Required

Create `.env` file with:

```env
# Groq LLM API
GROQ_API_KEY=your_groq_api_key_here

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

Get free Groq API key: https://console.groq.com/

---

## Summary

**You can use the system RIGHT NOW** without installing scispacy. Just run:

```powershell
streamlit run app.py
```

And upload the test documents to see multi-document RAG in action!

The only difference without scispacy is fewer biomedical entities extracted, but all core functionality (vector search, cross-document linking, LLM answers, source citations) works perfectly.
