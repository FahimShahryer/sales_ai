"""
RAG Service - FAISS Vector Database Retrieval
Retrieves relevant context from the knowledge base
"""
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings


class RAGService:
    """Service for retrieving context from FAISS vector database"""

    def __init__(self):
        """Initialize RAG service with FAISS vector store"""
        print("🔧 Initializing RAG Service...")

        # Load embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

        # Load FAISS index
        self.vectorstore = FAISS.load_local(
            str(settings.FAISS_INDEX_PATH),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        print("✅ RAG Service initialized successfully")

    def search(self, query: str, k: int = None) -> List[Dict]:
        """
        Search for relevant context in the knowledge base

        Args:
            query: User query or question
            k: Number of documents to retrieve (default from settings)

        Returns:
            List of relevant documents with content and metadata
        """
        if k is None:
            k = settings.RAG_TOP_K

        # Perform similarity search
        docs = self.vectorstore.similarity_search(query, k=k)

        # Format results
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })

        return results

    def get_context_string(self, query: str, k: int = None) -> str:
        """
        Get context as a formatted string for LLM prompts

        Args:
            query: User query
            k: Number of documents to retrieve

        Returns:
            Formatted context string
        """
        docs = self.search(query, k)

        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Context {i}]")
            context_parts.append(doc["content"])
            context_parts.append("")  # Empty line for separation

        return "\n".join(context_parts)

    def search_by_type(self, query: str, doc_type: str, k: int = 3) -> List[Dict]:
        """
        Search for documents of a specific type

        Args:
            query: Search query
            doc_type: Type of document (e.g., 'schema', 'product', 'knowledge')
            k: Number of results

        Returns:
            Filtered results matching the document type
        """
        # Get more results initially
        all_docs = self.search(query, k=k * 3)

        # Filter by type
        filtered = [doc for doc in all_docs if doc["metadata"].get("type") == doc_type]

        # Return top k
        return filtered[:k]
