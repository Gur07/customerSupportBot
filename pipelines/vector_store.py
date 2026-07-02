import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Dict
import os

class VectorStore:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """Initialize with a lightweight local embedding model (no API needed)"""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts locally (fast, no rate limits)"""
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.model.encode([query])[0]
    
    def build_index(self, chunks: List[Dict]):
        """Build FAISS index from chunks"""
        print("Building FAISS index with local embeddings...")
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embed_texts(texts)
        
        print("Creating FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✓ Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for top-k most similar chunks"""
        query_embedding = self.embed_query(query)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            chunk = self.chunks[idx].copy()
            chunk['similarity_score'] = float(1 / (1 + distance))
            results.append(chunk)
        
        return results
    
    def save(self, index_path='data/faiss_index.bin', metadata_path='data/chunks_metadata.pkl'):
        """Save FAISS index and metadata"""
        os.makedirs('data', exist_ok=True)
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        print(f"✓ Saved index to {index_path} and metadata to {metadata_path}")
    
    def load(self, index_path='data/faiss_index.bin', metadata_path='data/chunks_metadata.pkl'):
        """Load FAISS index and metadata"""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.chunks = pickle.load(f)
        print(f"✓ Loaded index with {self.index.ntotal} vectors")


# Load chunks
# with open('data/chunks.json', 'r', encoding='utf-8') as f:
#     chunks = json.load(f)

# # Build vector store with local embeddings (FAST!)
# vector_store = VectorStore()
# vector_store.build_index(chunks)
# vector_store.save()

# # Test search
# print("\n" + "="*80)
# print("Testing search...")
# print("="*80)
# results = vector_store.search("How do I connect Snowflake to Atlan?", k=5)
# print("\nTest search results:")
# for i, result in enumerate(results, 1):
#     print(f"\n{i}. {result['title']} (score: {result['similarity_score']:.3f})")
#     print(f"   URL: {result['url']}")
#     print(f"   Text preview: {result['text'][:150]}...")