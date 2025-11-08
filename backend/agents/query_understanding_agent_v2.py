"""
Query Understanding Agent - Fully Dynamic LLM-Driven
NO HARDCODING - Pure LLM analysis
"""
from typing import Dict, Any
import json
import re


class QueryUnderstandingAgent:
    """Fully dynamic query understanding using LLM"""

    def __init__(self, llm_service):
        self.llm = llm_service

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to deeply analyze user query
        NO hardcoded patterns or rules

        Args:
            query: Raw user query

        Returns:
            Comprehensive query analysis
        """
        print(f"\n🔍 [Query Understanding Agent] Analyzing: {query}")

        analysis_prompt = f"""You are a query analysis expert for a sales intelligence system.

USER QUERY: "{query}"

Analyze this query and provide a detailed breakdown in JSON format:

{{
    "is_greeting": "yes/no (if this is just a greeting like 'hi', 'hello', 'hey')",
    "is_data_query": "yes/no (if this requires data from the sales database)",
    "intent": "What is the user trying to do? (analyze/compare/predict/recommend/investigate/greet/other)",
    "question_type": "descriptive/diagnostic/predictive/prescriptive/conversational/greeting",
    "time_scope": {{
        "mentioned": "yes/no",
        "specific_periods": ["list any years, quarters, months, dates mentioned"],
        "comparison_needed": "yes/no (if comparing time periods)"
    }},
    "entities": {{
        "divisions": ["any divisions mentioned: FMCG, Cement, Textile, or null"],
        "products": ["any products mentioned or null"],
        "branches": ["any branches/locations mentioned or null"],
        "metrics": ["what to measure: sales, revenue, profit, margin, quantity, growth, etc."]
    }},
    "complexity": "simple/moderate/complex",
    "requires_comparison": "yes/no",
    "requires_calculation": "yes/no",
    "requires_forecasting": "yes/no",
    "requires_data_access": "yes/no (does this need to access the CSV data?)",
    "context_needed": ["what business context would help answer this?"],
    "data_requirements": "Describe what data is needed from CSV to answer this query (or 'none' if not applicable)",
    "suggested_approach": "How should this query be answered?"
}}

Return ONLY valid JSON, no explanation.
"""

        response = self.llm.generate(analysis_prompt)

        # Extract JSON
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"error": "Failed to parse", "raw_response": response}
        except Exception as e:
            analysis = {"error": str(e), "raw_response": response}

        print(f"✅ Query Analysis Complete")
        print(f"   Intent: {analysis.get('intent', 'unknown')}")
        print(f"   Type: {analysis.get('question_type', 'unknown')}")

        return {
            "query": query,
            "analysis": analysis,
            "success": "error" not in analysis
        }
