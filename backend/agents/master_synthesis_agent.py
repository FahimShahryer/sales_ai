"""
Master Synthesis Agent - Combines all data and generates final answer
Fully dynamic LLM-driven synthesis
"""
from typing import Dict, Any


class MasterSynthesisAgent:
    """Master agent that synthesizes all information into final answer"""

    def __init__(self, llm_service):
        self.llm = llm_service

    def synthesize_answer(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        retrieved_data: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize final answer from all sources

        Args:
            query: Original user query
            query_analysis: Analysis from QueryUnderstandingAgent
            retrieved_data: Data from DataRetrievalAgent
            rag_context: Context from RAGAgent

        Returns:
            Final synthesized answer
        """
        print(f"\n🎯 [Master Synthesis Agent] Synthesizing final answer...")

        try:
            # Build comprehensive prompt
            synthesis_prompt = self._build_synthesis_prompt(
                query,
                query_analysis,
                retrieved_data,
                rag_context
            )

            # Generate answer
            print(f"   Calling LLM to generate synthesis...")
            answer = self.llm.generate(synthesis_prompt)

            print(f"   LLM returned: {len(answer) if answer else 0} characters")

            if not answer or len(answer.strip()) == 0:
                print(f"   ❌ LLM returned empty answer!")
                print(f"   Prompt was: {len(synthesis_prompt)} chars")
                answer = "I was unable to generate a proper response. The LLM returned an empty answer. Please try a simpler query."

            print(f"✅ Final answer generated: {answer[:100]}...")

            # Determine agent type based on analysis
            agent_type = self._determine_agent_type(query_analysis)

            return {
                "success": True,
                "answer": answer,
                "agent": f"{agent_type} Agent",
                "query_type": f"{agent_type} Analytics",
                "data": None,
                "visualizations": []
            }

        except Exception as e:
            print(f"❌ Error in synthesis: {str(e)}")
            return {
                "success": False,
                "answer": f"I encountered an error while generating the answer: {str(e)}",
                "agent": "Error Handler",
                "query_type": "Error",
                "data": None,
                "visualizations": [],
                "error": str(e)
            }

    def _build_synthesis_prompt(
        self,
        query: str,
        query_analysis: Dict,
        retrieved_data: Dict,
        rag_context: Dict
    ) -> str:
        """Build comprehensive synthesis prompt"""

        # Format retrieved data
        data_section = self._format_data_section(retrieved_data)

        # Format RAG context (LIMIT to prevent overwhelming LLM!)
        raw_context = rag_context.get('context', 'No additional context available')

        # Limit RAG context to 4000 characters to prevent token overflow
        # (Increased from 2000 since max_tokens increased to 8000)
        if len(raw_context) > 4000:
            context_section = raw_context[:4000] + "\n... (truncated for brevity)"
            print(f"   ⚠️ RAG context truncated from {len(raw_context)} to 4000 chars")
        else:
            context_section = raw_context

        # Get question type
        question_type = query_analysis.get('analysis', {}).get('question_type', 'descriptive')

        # Build system prompt based on question type
        system_prompts = {
            'descriptive': """You are a Data Analyst answering "WHAT HAPPENED?" questions.
Focus on: Facts, summaries, totals, breakdowns, historical data.

PROFESSIONAL FORMATTING REQUIREMENTS:
- Use bullet points (•) for lists and rankings
- Use clear section headers when presenting multiple data points
- Use line breaks for readability
- Format numbers with proper separators (৳X,XXX,XXX)
- Present top/bottom rankings in order with rank numbers

Example format for rankings:
**Top 5 Products by Sales:**
1. Product A: ৳495.1M
2. Product B: ৳459.0M
3. Product C: ৳416.0M
4. Product D: ৳409.4M
5. Product E: ৳398.7M

**Key Insight:** All top performers are from the Cement Division

Example format for breakdowns:
**Revenue by Division (2024):**
• FMCG: ৳125.5M (35% of total)
• Cement: ৳180.2M (50% of total)
• Textile: ৳54.3M (15% of total)

**Total Revenue:** ৳360.0M""",

            'diagnostic': """You are a Detective Agent answering "WHY DID IT HAPPEN?" questions.
Focus on: Root causes, comparisons, correlations, business events, explanations.

PROFESSIONAL FORMATTING REQUIREMENTS:
- Use clear sections: **Root Cause**, **Analysis**, **Key Factors**
- Use bullet points (•) for multiple factors
- Show comparisons with specific numbers
- Use line breaks between sections

Example format for comparisons:
**Performance Comparison:**
• Branch A: ৳2.5M revenue, 12.3% margin
• Branch B: ৳1.8M revenue, 8.5% margin
• Difference: +38% revenue, +3.8% margin points

**Root Causes:**
1. Branch A has newer infrastructure
2. Higher customer traffic (35% more footfall)
3. Better product mix (60% high-margin items)

**Conclusion:** Branch A outperforms due to location and product strategy

Example format for trend analysis:
**Why Revenue Dropped in Q4:**

**Primary Factors:**
• Seasonal decline: 25% reduction typical for Q4
• Supply chain issues: 10-day stockout in key products
• Competition increase: 3 new competitors entered market

**Impact Breakdown:**
1. Seasonal effect: -৳15M (60% of decline)
2. Stockouts: -৳8M (32% of decline)
3. Competition: -৳2M (8% of decline)

**Total Decline:** ৳25M (-18% vs Q3)""",

            'predictive': """You are a Forecaster Agent answering "WHAT WILL HAPPEN?" questions.
Focus on: Trends, forecasts, projections, patterns, future predictions.

PROFESSIONAL FORMATTING REQUIREMENTS:
- Use clear sections: **Current Trend**, **Projection**, **Key Assumptions**
- Show trend data with arrows (↑ ↓ →)
- Include confidence levels or ranges where applicable
- Use bullet points for multiple projections

Example format for forecasts:
**Revenue Forecast for 2026:**

**Current Trend (2023-2025):**
• 2023: ৳280M
• 2024: ৳325M (+16% growth)
• 2025: ৳370M (projected, +14% growth)

**2026 Projection:** ৳420M - ৳435M
• Conservative: ৳420M (+14% growth)
• Expected: ৳428M (+16% growth)
• Optimistic: ৳435M (+18% growth)

**Key Drivers:**
1. Market expansion continuing (↑)
2. New branch ramp-ups maturing (↑)
3. Economic conditions stable (→)

**Confidence Level:** High (based on 3-year consistent growth pattern)

Example format for trend identification:
**Product Trends:**

**📈 Growing (>15% YoY):**
• Product A: +22% growth, momentum strong
• Product B: +18% growth, new market entry

**→ Stable (±5% YoY):**
• Product C: +3% growth, mature market
• Product D: -2% decline, seasonal variation

**📉 Declining (>10% drop):**
• Product E: -15% decline, market saturation
• Product F: -12% decline, competition increase""",

            'prescriptive': """You are a Strategic Business Analyst providing DATA-DRIVEN recommendations.

🎯 METHODOLOGY FOR STRATEGIC RECOMMENDATIONS:

1. ANALYZE THE DATA:
   - Identify if the entity exists in the data (e.g., does "Khulna branch" exist?)
   - If NO: Use comparable entity data for benchmarking
   - Extract key metrics: revenue, profit margins, growth rates, market share

2. MAKE COMPARISONS:
   - Compare similar entities (e.g., tier-2 city branches)
   - Identify best performers and why they succeed
   - Calculate specific metrics (ROI, payback period, profit margins)

3. ASSESS MARKET OPPORTUNITY:
   - Analyze market gaps (underserved regions/segments)
   - Check market saturation (# of branches per division)
   - Identify high-potential divisions/products

4. PROVIDE SPECIFIC RECOMMENDATION:
   - Clear YES/NO/CONDITIONAL recommendation
   - SPECIFIC NUMBERS: projected revenue, profit margins, investment estimates
   - Risk factors and mitigation strategies
   - Timeline and implementation steps

5. ANSWER FORMAT:
   **Recommendation: [YES/NO/CONDITIONAL] - [Action]**

   **Data-Driven Analysis:**
   - [Metric 1 with specific numbers from comparable entities]
   - [Metric 2 with market opportunity assessment]
   - [Metric 3 with profitability indicators]

   **Projected Outcome:** [Specific revenue/profit projections based on benchmarks]

   **Conditions/Risks:** [If conditional, what needs to be validated first]

6. BE SPECIFIC:
   - Use actual numbers from the data (৳X revenue, Y% margin)
   - Reference comparable entities by name
   - Give concrete projections based on benchmarks
   - NO vague statements like "conduct feasibility study" without data-backed reasoning

7. NEVER SAY:
   ❌ "Cannot make recommendation without data" (USE COMPARABLE DATA!)
   ❌ "Conduct market research first" (GIVE recommendation based on available data)
   ❌ "May be profitable" (BE SPECIFIC with projections)

8. ALWAYS INCLUDE:
   ✅ Specific comparable entity performance
   ✅ Numerical projections based on benchmarks
   ✅ Clear recommendation with reasoning
   ✅ Risk assessment based on data patterns"""
        }

        system_prompt = system_prompts.get(question_type, system_prompts['descriptive'])

        # Build question-type specific instructions
        if question_type == 'prescriptive':
            specific_instructions = """
STRATEGIC RECOMMENDATION INSTRUCTIONS:
1. Start with clear recommendation: "Recommendation: YES/NO/CONDITIONAL - [specific action]"
2. Provide 3-4 data-backed bullet points with SPECIFIC NUMBERS from the retrieved data
3. Include projected outcome with concrete numbers (revenue, margin, timeline)
4. If comparable entity data is provided, USE IT for projections
5. Mention specific risks/conditions based on data patterns
6. Use Bangladesh currency (৳) for all monetary values
7. Keep total response to 5-7 sentences maximum
8. NO vague statements - every claim must reference specific data
9. Format: **Recommendation:** [decision], **Analysis:** [3-4 bullets], **Projection:** [numbers]

Example format:
**Recommendation: YES - Open FMCG Branch in Khulna**

**Data-Driven Analysis:**
- FMCG Sylhet (comparable tier-2 city) generates ৳2.5M monthly with 12.3% profit margin
- Khulna region currently underserved (nearest branch 250km away)
- FMCG division shows highest profitability (14.2% avg margin) with only 4 branches

**Projected Outcome:** ৳2.2M monthly revenue, 18-month payback period based on Sylhet ramp-up pattern

**Risk Mitigation:** Ensure logistics from Dhaka hub, start with top 10 SKUs only
"""
        else:
            specific_instructions = """
🎯 CRITICAL FORMATTING REQUIREMENTS - FOLLOW THIS EXACT TEMPLATE:

For TOP/RANKING queries (top products, top branches, etc):
**Top 5 [Items] by [Metric]:**
1. Item A: ৳495.1M
2. Item B: ৳459.0M
3. Item C: ৳416.0M
4. Item D: ৳409.4M
5. Item E: ৳398.7M

**Key Insight:** [One sentence observation]

For BREAKDOWN queries (division breakdown, revenue by category):
**Revenue by Division (2024):**
• FMCG: ৳125.5M (35%)
• Cement: ৳180.2M (50%)
• Textile: ৳54.3M (15%)

**Total Revenue:** ৳360.0M

MANDATORY FORMATTING RULES:
✅ Use bold headers: **Header:**
✅ Use numbered lists for rankings: 1. 2. 3.
✅ Format numbers in millions: ৳495.1M (NOT ৳495,139,517)
✅ Add blank line after header
✅ End with **Key Insight:** or **Total:**
❌ NO paragraphs or prose
❌ NO full numbers like ৳495,139,517.63
❌ NO preambles
"""

        full_prompt = f"""{ specific_instructions}

{'='*70}
{system_prompt}
{'='*70}

USER QUERY:
{query}

RETRIEVED DATA FROM CSV:
{data_section}

BUSINESS CONTEXT FROM KNOWLEDGE BASE:
{context_section}

IMPORTANT:
1. Follow the formatting requirements EXACTLY as shown above
2. Do NOT write paragraphs - use the structured format
3. Generate your formatted answer now:
"""

        print(f"   Final prompt length: {len(full_prompt)} characters")

        return full_prompt

    def _format_data_section(self, retrieved_data: Dict) -> str:
        """Format retrieved data into readable text"""

        if not retrieved_data.get('success'):
            return f"Data Retrieval Failed: {retrieved_data.get('error', 'Unknown error')}"

        data = retrieved_data.get('data', {})
        data_type = data.get('type', 'unknown')

        if data_type == 'scalar':
            return f"Result: ৳{data.get('value', 0):,.0f}"

        elif data_type == 'dict':
            dict_data = data.get('data', {})
            lines = []

            # Check if this is strategic analysis data (has nested dicts)
            has_nested = any(isinstance(v, dict) for v in dict_data.values())

            if has_nested:
                # Format strategic/comparative data more clearly
                lines.append("STRATEGIC ANALYSIS DATA:")
                lines.append("="*60)

                for key, value in dict_data.items():
                    if isinstance(value, dict):
                        lines.append(f"\n📊 {key.upper().replace('_', ' ')}:")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                lines.append(f"   • {sub_key}:")
                                for k, v in sub_value.items():
                                    if isinstance(v, (int, float)):
                                        if v > 1000:
                                            lines.append(f"     - {k}: ৳{v:,.0f}")
                                        else:
                                            lines.append(f"     - {k}: {v:.2f}")
                                    else:
                                        lines.append(f"     - {k}: {v}")
                            elif isinstance(sub_value, (int, float)):
                                if sub_value > 1000:
                                    lines.append(f"   • {sub_key}: ৳{sub_value:,.0f}")
                                else:
                                    lines.append(f"   • {sub_key}: {sub_value:.2f}")
                            else:
                                lines.append(f"   • {sub_key}: {sub_value}")
                    elif isinstance(value, (int, float)):
                        if value > 1000:
                            lines.append(f"• {key}: ৳{value:,.0f}")
                        else:
                            lines.append(f"• {key}: {value:.2f}")
                    else:
                        lines.append(f"• {key}: {value}")

                return "\n".join(lines)
            else:
                # Simple dict formatting
                for key, value in dict_data.items():
                    if isinstance(value, (int, float)):
                        if value > 1000:
                            lines.append(f"  - {key}: ৳{value:,.0f}")
                        else:
                            lines.append(f"  - {key}: {value:.2f}")
                    else:
                        lines.append(f"  - {key}: {value}")
                return "Data Retrieved:\n" + "\n".join(lines)

        elif data_type == 'dataframe':
            df_data = data.get('data', [])
            if len(df_data) > 0:
                # Show first few rows
                lines = ["Data Retrieved:"]
                for i, row in enumerate(df_data[:10], 1):
                    row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    lines.append(f"  [{i}] {row_str}")
                if len(df_data) > 10:
                    lines.append(f"  ... ({len(df_data)} total rows)")
                return "\n".join(lines)
            else:
                return "No data found matching the criteria"

        elif data_type == 'list':
            list_data = data.get('data', [])
            return f"Data Retrieved: {list_data}"

        else:
            return f"Data: {data.get('data', 'No data')}"

    def _determine_agent_type(self, query_analysis: Dict) -> str:
        """Determine which agent type to display"""

        question_type = query_analysis.get('analysis', {}).get('question_type', 'descriptive')

        type_mapping = {
            'descriptive': 'Data Analyst',
            'diagnostic': 'Detective',
            'predictive': 'Forecaster',
            'prescriptive': 'Strategist'
        }

        return type_mapping.get(question_type, 'Data Analyst')
