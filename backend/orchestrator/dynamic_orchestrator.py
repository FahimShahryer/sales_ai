"""
Fully Dynamic Multi-Agent Orchestrator
NO HARDCODING - Everything LLM-driven
"""
from typing import Dict, Any
from backend.agents.query_understanding_agent_v2 import QueryUnderstandingAgent
from backend.agents.data_retrieval_agent_v2 import DataRetrievalAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.master_synthesis_agent import MasterSynthesisAgent


class DynamicOrchestrator:
    """
    Fully dynamic orchestrator - Zero hardcoding
    Everything is LLM-driven and adaptive
    """

    def __init__(self, rag_service, data_service, llm_service):
        """Initialize all dynamic agents"""
        print("\n" + "=" * 80)
        print("🚀 INITIALIZING FULLY DYNAMIC MULTI-AGENT SYSTEM")
        print("=" * 80)

        self.rag_service = rag_service
        self.data_service = data_service
        self.llm_service = llm_service

        # Initialize agents
        print("\n📦 Initializing Dynamic Agents...")

        self.query_understanding = QueryUnderstandingAgent(llm_service)
        print("  ✅ Query Understanding Agent (LLM-driven)")

        self.data_retrieval = DataRetrievalAgent(data_service, llm_service)
        print("  ✅ Data Retrieval Agent (LLM generates pandas code)")

        self.rag_agent = RAGAgent(rag_service, llm_service)
        print("  ✅ RAG Agent (Dynamic FAISS search)")

        self.master_synthesis = MasterSynthesisAgent(llm_service)
        print("  ✅ Master Synthesis Agent (LLM-driven)")

        print("\n" + "=" * 80)
        print("✅ DYNAMIC ORCHESTRATOR READY")
        print("   🔹 Zero hardcoded queries")
        print("   🔹 LLM generates all code")
        print("   🔹 Fully adaptive system")
        print("=" * 80 + "\n")

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process query through fully dynamic pipeline

        Pipeline:
        1. Query Understanding (LLM) → Deep analysis
        2. Data Retrieval (LLM) → Generate & execute pandas code
        3. RAG Agent (LLM) → Retrieve relevant context
        4. Master Synthesis (LLM) → Combine & generate answer

        Args:
            query: User query

        Returns:
            Final response with answer
        """
        print("\n" + "=" * 80)
        print(f"📥 PROCESSING QUERY: {query}")
        print("=" * 80)

        try:
            # STEP 1: Understand Query (LLM-driven)
            print("\n🔍 STEP 1: Understanding Query with LLM...")
            query_analysis = self.query_understanding.analyze_query(query)

            if not query_analysis.get('success'):
                return self._error_response("Query analysis failed")

            analysis = query_analysis.get('analysis', {})

            # Check if this is a greeting or non-data query
            is_greeting = analysis.get('is_greeting', 'no') == 'yes'
            is_data_query = analysis.get('is_data_query', 'yes') == 'yes'
            requires_data = analysis.get('requires_data_access', 'yes') == 'yes'

            # Handle greetings and non-data queries
            if is_greeting or not is_data_query or not requires_data:
                print("✅ Detected greeting/conversational query - skipping data retrieval")
                return self._handle_conversational_query(query, query_analysis)

            # STEP 2: Retrieve RAG Context FIRST (schema, columns, business context)
            print("\n📚 STEP 2: Retrieving Knowledge Base Context (schema, columns, business info)...")
            try:
                rag_context = self.rag_agent.retrieve_context(query, query_analysis)
            except Exception as rag_error:
                print(f"⚠️  RAG retrieval had issues: {str(rag_error)}")
                rag_context = {
                    "success": False,
                    "context": "Unable to retrieve business context",
                    "raw_documents": {}
                }

            # STEP 3: Retrieve Data (LLM generates pandas code WITH RAG context)
            print("\n📊 STEP 3: Retrieving Data (LLM generates code with full context)...")
            retrieved_data = self.data_retrieval.retrieve_data(query, query_analysis, rag_context)

            # Even if data retrieval fails, continue to synthesis
            if not retrieved_data.get('success'):
                print(f"⚠️  Data retrieval had issues: {retrieved_data.get('error')}")

            # STEP 4: Synthesize Final Answer (LLM combines everything)
            print("\n🎯 STEP 4: Synthesizing Final Answer with LLM...")
            final_response = self.master_synthesis.synthesize_answer(
                query=query,
                query_analysis=query_analysis,
                retrieved_data=retrieved_data,
                rag_context=rag_context
            )

            print("\n" + "=" * 80)
            print("✅ QUERY PROCESSED SUCCESSFULLY")
            print("=" * 80 + "\n")

            return final_response

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

            return self._error_response(f"Processing error: {str(e)}")

    def _handle_conversational_query(self, query: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greetings and conversational queries without data retrieval"""

        conversational_prompt = f"""You are a friendly sales intelligence assistant for Akij Group.

USER QUERY: "{query}"

This is a conversational query (greeting or general question), not a data analytics request.

Respond in a helpful, professional manner. Keep it brief (2-3 sentences).

Suggestions you can mention:
- I can help analyze sales data across FMCG, Cement, Textile, and Tobacco divisions
- I can answer questions about revenue, trends, comparisons, and forecasts
- I can provide insights about specific time periods, products, or branches

Generate a natural, friendly response:
"""

        answer = self.llm_service.generate(conversational_prompt)

        return {
            "success": True,
            "answer": answer,
            "agent": "Conversational Assistant",
            "query_type": "Greeting/Conversational",
            "data": None,
            "visualizations": [],
            "skipped_data_retrieval": True
        }

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "success": False,
            "answer": f"I encountered an error: {error_message}",
            "agent": "System",
            "query_type": "Error",
            "data": None,
            "visualizations": [],
            "error": error_message
        }
