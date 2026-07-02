"""
One-time setup script to build RAG pipeline
Run this once before starting the Streamlit app
"""

import os
from pipelines.doc_ingestion import AtlanDocsCrawler
from pipelines.doc_chunking import DocumentChunker
from pipelines.vector_store import VectorStore
import json

def main():
    print("=" * 80)
    print("ATLAN HELPDESK RAG PIPELINE SETUP")
    print("=" * 80)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Step 1: Crawl documentation
    print("\n[1/3] Crawling Atlan documentation...")
    print("This may take a few minutes...")
    crawler = AtlanDocsCrawler(max_pages=50)
    docs = crawler.crawl()
    crawler.save_docs()
    print(f"✓ Crawled {len(docs)} pages")
    
    # Step 2: Chunk documents
    print("\n[2/3] Chunking documents...")
    with open('data/raw_docs.json', 'r', encoding='utf-8') as f:
        docs = json.load(f)
    
    chunker = DocumentChunker(chunk_size=500, overlap=100)
    chunks = chunker.process_documents(docs)
    chunker.save_chunks(chunks)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Step 3: Build vector store
    print("\n[3/3] Building FAISS vector store...")
    print("Downloading embedding model (first time only)...")
    with open('data/chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    vector_store = VectorStore()
    vector_store.build_index(chunks)
    vector_store.save()
    print(f"✓ Vector store built with {len(chunks)} vectors")
    
    print("\n" + "=" * 80)
    print("✓ RAG PIPELINE SETUP COMPLETE!")
    print("=" * 80)
    print("\nYou can now run the Streamlit app:")
    print("  streamlit run app.py")
    print("\nFiles created:")
    print("  - data/raw_docs.json")
    print("  - data/chunks.json")
    print("  - data/faiss_index.bin")
    print("  - data/chunks_metadata.pkl")


if __name__ == "__main__":
    main()