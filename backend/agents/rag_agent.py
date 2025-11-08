"""
RAG Agent - Retrieves relevant business context
Fully dynamic FAISS search
"""
from typing import Dict, Any, List
import json
import re


class RAGAgent:
    """Agent for retrieving relevant context from FAISS vector database"""

    def __init__(self, rag_service, llm_service):
        self.rag = rag_service
        self.llm = llm_service

    def retrieve_context(self, query: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant business context from FAISS

        Args:
            query: Original user query
            query_analysis: Query analysis from understanding agent

        Returns:
            Retrieved context
        """
        print(f"\n📚 [RAG Agent] Retrieving context from knowledge base...")

        # Determine what type of context is needed
        context_types = self._determine_context_types(query, query_analysis)

        print(f"   Context types needed: {', '.join(context_types)}")

        all_context = {}

        # Retrieve different types of context
        for context_type in context_types:
            # Retrieve MORE documents for schema and products (they're critical!)
            if context_type in ['schema', 'products']:
                docs = self._search_by_type(query, context_type, k=5)
            else:
                docs = self._search_by_type(query, context_type, k=3)

            if docs:
                all_context[context_type] = docs

        # Format context
        formatted_context = self._format_context(all_context)

        print(f"✅ Retrieved {sum(len(v) for v in all_context.values())} relevant documents")

        return {
            "success": True,
            "context": formatted_context,
            "raw_documents": all_context
        }

    def _determine_context_types(self, query: str, analysis: Dict) -> List[str]:
        """Use LLM to determine what types of context are needed

        IMPORTANT: Schema and products are ALWAYS included for data queries
        """

        context_prompt = f"""Given this query and analysis, determine what types of business context would be helpful.

QUERY: "{query}"

ANALYSIS:
{json.dumps(analysis.get('analysis', {}), indent=2)}

Available context types:
- schema: Database schema, column descriptions, table structure (CRITICAL for pandas code generation!)
- products: Product information and catalog (CRITICAL for product queries!)
- business_events: Historical business events (supply shortages, price wars, etc.)
- seasonal_patterns: Seasonal trends (Eid, monsoon, construction season)
- relationships: Relationships between data entities
- query_examples: Example queries and patterns

IMPORTANT: For ANY data query, ALWAYS include "schema" and "products" first!

Which context types are most relevant? Return as a JSON list with schema and products first.

Example: {{"context_types": ["schema", "products", "business_events", "seasonal_patterns"]}}

Return ONLY valid JSON.
"""

        response = self.llm.generate(context_prompt)

        # Extract context types
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                context_types = result.get('context_types', [])
            else:
                # Default fallback - ALWAYS include schema and products
                context_types = ["schema", "products", "business_events"]
        except:
            # Default fallback - ALWAYS include schema and products
            context_types = ["schema", "products", "business_events"]

        # Ensure schema and products are always first for data queries
        if 'schema' not in context_types:
            context_types.insert(0, 'schema')
        if 'products' not in context_types:
            context_types.insert(1, 'products')

        return context_types

    def _search_by_type(self, query: str, doc_type: str, k: int = 3) -> List[str]:
        """Search for specific document type"""

        # Search FAISS for relevant documents
        docs = self.rag.search_by_type(query, doc_type, k=k)

        if not docs:
            # Fallback to general search
            docs = self.rag.search(query, k=k)

        return [doc.get('content', '') for doc in docs if doc.get('content')]

    def _format_context(self, all_context: Dict[str, List[str]]) -> str:
        """Format retrieved context into readable text"""

        formatted_parts = []

        for context_type, documents in all_context.items():
            formatted_parts.append(f"\n=== {context_type.upper().replace('_', ' ')} ===")
            for i, doc in enumerate(documents, 1):
                formatted_parts.append(f"\n[{i}] {doc}")

        return "\n".join(formatted_parts)
