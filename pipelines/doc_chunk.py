import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import os

class DocumentChunker:
    def __init__(self, chunk_size=500, overlap=100):
        """Initialize with LangChain's RecursiveCharacterTextSplitter"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks using LangChain splitter"""
        return self.text_splitter.split_text(text)
    
    def process_documents(self, docs: List[Dict]) -> List[Dict]:
        """Process all documents and create chunks with metadata"""
        all_chunks = []
        chunk_id = 0
        
        for doc in docs:
            text_chunks = self.chunk_text(doc['text'])
            
            for i, chunk in enumerate(text_chunks):
                all_chunks.append({
                    'chunk_id': chunk_id,
                    'url': doc['url'],
                    'title': doc['title'],
                    'text': chunk,
                    'chunk_index': i,
                    'total_chunks': len(text_chunks)
                })
                chunk_id += 1
        
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], filename='data/chunks.json'):
        """Save chunks to JSON"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(chunks)} chunks to {filename}")



# Load raw docs
with open('data/raw_docs.json', 'r', encoding='utf-8') as f:
    docs = json.load(f)

# Chunk documents using LangChain
chunker = DocumentChunker(chunk_size=500, overlap=100)
chunks = chunker.process_documents(docs)
chunker.save_chunks(chunks)

print(f"Total chunks created: {len(chunks)}")
print(f"Average chunks per document: {len(chunks)/len(docs):.2f}")

# Show sample chunk
if chunks:
    print(f"\nSample chunk:")
    print(f"Title: {chunks[0]['title']}")
    print(f"Text length: {len(chunks[0]['text'])} chars")
    print(f"Text preview: {chunks[0]['text'][:200]}...")