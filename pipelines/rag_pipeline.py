from pipelines.vector_store import VectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class RAGPipeline:
    def __init__(self):
        """Initialize RAG pipeline with vector store and LLM"""
        self.vector_store = VectorStore()
        self.vector_store.load()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant chunks for query"""
        return self.vector_store.search(query, k=k)
    
    def build_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        """Build prompt with retrieved context"""
        context_text = "\n\n".join([
            f"[Source {i+1}] {chunk['title']}\nURL: {chunk['url']}\nContent: {chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        prompt = f"""You are a helpful assistant for Atlan support tickets. Answer the user's question using ONLY the provided documentation context below.

CONTEXT FROM DOCUMENTATION:
{context_text}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question concisely and accurately using ONLY information from the provided context
2. If the answer is not found in the context, explicitly say "Not found in docs"
3. Include a SOURCES section at the end listing all URLs you referenced
4. Be specific and cite which source number you're using for each claim

ANSWER:"""
        
        return prompt
    
    def generate_answer(self, query: str) -> Dict:
        """Generate answer using RAG pipeline"""
        # Retrieve relevant chunks
        context_chunks = self.retrieve_context(query, k=5)
        
        # Build prompt
        prompt = self.build_prompt(query, context_chunks)
        
        # Generate response
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Extract sources from context
            sources = []
            seen_urls = set()
            for chunk in context_chunks:
                if chunk['url'] not in seen_urls:
                    sources.append({
                        'url': chunk['url'],
                        'title': chunk['title'],
                        'score': chunk['similarity_score']
                    })
                    seen_urls.add(chunk['url'])
            
            return {
                'answer': answer,
                'sources': sources,
                'context_chunks': context_chunks
            }
            
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'context_chunks': context_chunks
            }
    
    def query(self, question: str) -> Dict:
        """Main query interface"""
        return self.generate_answer(question)


# rag = RAGPipeline()

# # Test queries
# test_queries = [
#     "How do I connect Snowflake to Atlan?",
#     "What permissions are needed for Snowflake integration?",
#     "How does lineage work in Atlan?"
# ]

# for query in test_queries:
#     print(f"\n{'='*80}")
#     print(f"QUERY: {query}")
#     print('='*80)
    
#     result = rag.query(query)
#     print(f"\nANSWER:\n{result['answer']}")
#     print(f"\nSOURCES ({len(result['sources'])}):")
#     for i, source in enumerate(result['sources'], 1):
#         print(f"{i}. {source['title']}")
#         print(f"   {source['url']}")
#         print(f"   Relevance: {source['score']:.3f}")