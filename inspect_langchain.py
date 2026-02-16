
import langchain
print(f"LangChain version: {langchain.__version__}")
try:
    import langchain.chains
    print("langchain.chains found")
    print("Attributes in langchain.chains:", dir(langchain.chains))
except ImportError:
    print("langchain.chains NOT found")

try:
    from langchain.chains.combine_documents import create_stuff_documents_chain
    print("SUCCESS: from langchain.chains.combine_documents import create_stuff_documents_chain")
except ImportError as e:
    print(f"FAILED combine_documents: {e}")

try:
    from langchain.chains import create_retrieval_chain
    print("SUCCESS: from langchain.chains import create_retrieval_chain")
except ImportError as e:
    print(f"FAILED create_retrieval_chain: {e}")
