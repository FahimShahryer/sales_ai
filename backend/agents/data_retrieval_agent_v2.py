"""
Data Retrieval Agent - Fully Dynamic LLM-Driven
NO HARDCODING - LLM generates pandas code dynamically
"""
from typing import Dict, Any
import pandas as pd
import traceback
import json
import re


class DataRetrievalAgent:
    """Fully dynamic data retrieval using LLM to generate pandas code"""

    def __init__(self, data_service, llm_service):
        self.data = data_service
        self.llm = llm_service

    def retrieve_data(self, query: str, query_analysis: Dict[str, Any], rag_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use LLM to generate pandas code dynamically with RAG context
        NO hardcoded queries - pure LLM code generation

        Args:
            query: Original user query
            query_analysis: Analysis from QueryUnderstandingAgent
            rag_context: RAG context with schema, columns, business info (IMPORTANT!)

        Returns:
            Retrieved data results
        """
        print(f"\n📊 [Data Retrieval Agent] Retrieving data with full context...")

        try:
            df = self.data.get_dataframe()

            if df is None or df.empty:
                return {
                    "success": False,
                    "error": "DataFrame is empty or not available",
                    "data": None
                }

            # Get column information dynamically
            column_info = self._get_column_info(df)

            # Extract RAG context for better code generation
            rag_info = ""
            if rag_context and rag_context.get('success'):
                rag_info = rag_context.get('context', '')
                if rag_info:
                    print(f"   ✅ Using {len(rag_info)} chars of RAG context (schema + business info)")

            # Generate pandas code using LLM (with retry on failure)
            pandas_code = self._generate_pandas_code(query, query_analysis, column_info, rag_info)

            if not pandas_code:
                return {
                    "success": False,
                    "error": "Failed to generate pandas code",
                    "data": None
                }

            print(f"📝 Generated Pandas Code:\n{pandas_code}\n")

            # Validate the code first
            validation_error = self._validate_code(pandas_code)
            if validation_error:
                print(f"⚠️  Code validation failed: {validation_error}")
                print(f"🔄 Retrying code generation with simplified requirements...")

                # Retry with simpler prompt
                pandas_code = self._generate_simple_code(query, query_analysis, column_info, rag_info)

                if not pandas_code:
                    return {
                        "success": False,
                        "error": f"Code validation failed: {validation_error}. Retry also failed.",
                        "data": None
                    }

                print(f"📝 Regenerated Pandas Code:\n{pandas_code}\n")

            # Execute the generated code
            result = self._execute_pandas_code(pandas_code, df)

            return result

        except Exception as e:
            error_msg = f"Data retrieval error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "data": None,
                "traceback": traceback.format_exc()
            }

    def _get_column_info(self, df: pd.DataFrame) -> str:
        """Get dynamic column information from DataFrame"""
        try:
            # Basic dataset info
            info = f"""
Dataset Information:
- Total Rows: {len(df):,}
"""

            # Try to add date range if Date column exists
            if 'Date' in df.columns:
                try:
                    info += f"- Date Range: {df['Date'].min()} to {df['Date'].max()}\n"
                except:
                    pass

            info += "\nAvailable Columns:\n"

            for col in df.columns:
                try:
                    dtype = df[col].dtype
                    unique_count = df[col].nunique()

                    if dtype == 'object':
                        sample_values = df[col].unique()[:5].tolist()
                        info += f"  - {col} ({dtype}): {unique_count} unique values, samples: {sample_values}\n"
                    elif col in ['Year', 'Quarter', 'Month']:
                        unique_vals = sorted(df[col].unique().tolist())
                        info += f"  - {col} ({dtype}): values: {unique_vals}\n"
                    else:
                        info += f"  - {col} ({dtype}): numeric column\n"
                except Exception as col_error:
                    info += f"  - {col}: (error reading column)\n"

            return info
        except Exception as e:
            return f"Error getting column info: {str(e)}"

    def _generate_pandas_code(self, query: str, analysis: Dict, column_info: str, rag_info: str = "") -> str:
        """Use LLM to generate pandas code dynamically with RAG context"""

        # Build comprehensive context
        context_section = f"{column_info}"

        if rag_info:
            context_section += f"\n\n{'='*60}\nKNOWLEDGE BASE CONTEXT (Schema, Products, Business Info):\n{'='*60}\n{rag_info}\n{'='*60}\n"

        # Determine if this is a strategic/prescriptive query
        question_type = analysis.get('analysis', {}).get('question_type', 'descriptive')
        is_strategic = question_type == 'prescriptive'

        # Build predictive/trend guidance section for "predictive" queries
        predictive_guidance = ""
        if question_type == 'predictive':
            predictive_guidance = f"""
{'='*70}
📈 PREDICTIVE/TREND ANALYSIS REQUIREMENTS:
{'='*70}
This is a PREDICTIVE query about trends, forecasts, or patterns.

For "Which products/branches/divisions are trending upward/downward?":

1. CALCULATE YEAR-OVER-YEAR GROWTH RATES:
   - Group by entity (Product_Name, Branch_Name, Division_Name) and Year
   - Calculate total sales for each year
   - Compute growth rate between years
   - Identify positive trends (>10% growth), stable (±10%), declining (<-10%)

2. Example - "Which products are trending upward?":
```python
# Calculate yearly sales by product
yearly_sales = df.groupby(['Product_Name', 'Year'])['Net_Amount_BDT'].sum().reset_index()

# Calculate year-over-year growth for each product
growth_data = []
for product in yearly_sales['Product_Name'].unique():
    product_sales = yearly_sales[yearly_sales['Product_Name'] == product].sort_values('Year')

    if len(product_sales) >= 2:
        latest_year = product_sales.iloc[-1]
        previous_year = product_sales.iloc[-2]

        growth_rate = ((latest_year['Net_Amount_BDT'] / previous_year['Net_Amount_BDT']) - 1) * 100

        growth_data.append({{
            'Product_Name': product,
            'Latest_Year': int(latest_year['Year']),
            'Latest_Sales': float(latest_year['Net_Amount_BDT']),
            'Previous_Year': int(previous_year['Year']),
            'Previous_Sales': float(previous_year['Net_Amount_BDT']),
            'Growth_Rate_%': round(growth_rate, 2)
        }})

# Filter for upward trending products (growth > 0)
result = sorted(growth_data, key=lambda x: x['Growth_Rate_%'], reverse=True)
result = [p for p in result if p['Growth_Rate_%'] > 0][:10]
```

3. For "What is the trend of [specific product]?":
```python
product_data = df[df['Product_Name'] == 'Chanachur Mix']
monthly_trend = product_data.groupby(['Year', 'Month'])['Net_Amount_BDT'].sum().reset_index()
monthly_trend = monthly_trend.sort_values(['Year', 'Month'])
result = monthly_trend.to_dict('records')
```

4. For seasonal patterns:
```python
product_data = df[df['Product_Name'] == 'Chanachur Mix']
seasonal = product_data.groupby(['Quarter'])['Net_Amount_BDT'].mean().reset_index()
result = seasonal.to_dict('records')
```

5. For forecasting next year (simple linear projection):
```python
# Get historical yearly totals
yearly = df.groupby('Year')['Net_Amount_BDT'].sum().reset_index()
yearly = yearly.sort_values('Year')

# Calculate average growth rate
if len(yearly) >= 2:
    growth_rates = []
    for i in range(1, len(yearly)):
        rate = ((yearly.iloc[i]['Net_Amount_BDT'] / yearly.iloc[i-1]['Net_Amount_BDT']) - 1) * 100
        growth_rates.append(rate)

    avg_growth = sum(growth_rates) / len(growth_rates)
    latest_sales = yearly.iloc[-1]['Net_Amount_BDT']
    next_year = int(yearly.iloc[-1]['Year']) + 1

    result = {{
        'latest_year': int(yearly.iloc[-1]['Year']),
        'latest_sales': float(latest_sales),
        'avg_growth_rate_%': round(avg_growth, 2),
        'projected_year': next_year,
        'projected_sales': float(latest_sales * (1 + avg_growth/100))
    }}
```

CRITICAL: For trend analysis, you MUST calculate growth rates or time-series comparisons!
{'='*70}
"""

        # Build strategic guidance section for "prescriptive" queries
        strategic_guidance = ""
        if is_strategic:
            strategic_guidance = f"""
{'='*70}
🎯 STRATEGIC ANALYSIS REQUIREMENTS (for recommendations/decisions):
{'='*70}
This is a STRATEGIC/PRESCRIPTIVE query. Generate code that provides COMPARATIVE and ANALYTICAL data.

When answering strategic questions like "Should we open/expand/invest?":

1. CHECK IF ENTITY EXISTS in data first
   Example: khulna_exists = df[df['Branch_Name'].str.contains('Khulna', case=False)].shape[0] > 0

2. IF ENTITY DOESN'T EXIST (e.g., new branch location):
   - Find COMPARABLE entities (similar branches, products, markets)
   - Calculate their performance metrics (revenue, profit margin, growth rate)
   - Calculate market gaps and opportunities
   - Provide benchmark data for projections

3. MUST INCLUDE for expansion decisions:
   a) Comparable entity performance (e.g., similar branch metrics)
   b) Division/category profitability analysis
   c) Market saturation analysis (branch count, coverage)
   d) Growth trends of comparable entities
   e) Profit margins and ROI indicators

4. Strategic Query Example - "Should we open a branch in Khulna?":
```python
# Check if Khulna branch exists
khulna_exists = df[df['Branch_Name'].str.contains('Khulna', case=False)].shape[0] > 0

# Find comparable tier-2 city branches (Sylhet is similar to Khulna)
sylhet_branch = df[df['Branch_Name'] == 'FMCG Sylhet']
rajshahi_branch = df[df['Branch_Name'] == 'Cement Rajshahi']

# Calculate comparable branch performance
sylhet_metrics = sylhet_branch.groupby('Year').agg({{
    'Net_Amount_BDT': 'sum',
    'Profit_BDT': 'sum',
    'Margin_Percent': 'mean'
}}).to_dict('index')

# Analyze division profitability (which division should we open in Khulna?)
division_performance = df.groupby('Division_Name').agg({{
    'Net_Amount_BDT': 'sum',
    'Profit_BDT': 'sum',
    'Margin_Percent': 'mean',
    'Branch_ID': 'nunique'
}}).sort_values('Margin_Percent', ascending=False).to_dict('index')

# Market saturation analysis
branches_per_division = df.groupby('Division_Name')['Branch_Name'].nunique().to_dict()

# Growth rate of newest branches (to project Khulna ramp-up)
recent_branches = df[df['Branch_Name'].isin(['FMCG Sylhet'])].groupby(['Year', 'Month']).agg({{
    'Net_Amount_BDT': 'sum',
    'Profit_BDT': 'sum'
}}).reset_index().to_dict('records')

result = {{
    'khulna_exists': khulna_exists,
    'comparable_sylhet': sylhet_metrics,
    'division_profitability': division_performance,
    'market_saturation': branches_per_division,
    'ramp_up_pattern': recent_branches,
    'analysis_type': 'strategic_expansion'
}}
```

5. For "Which division/product should we focus on?":
   - Compare ALL options on multiple metrics
   - Include profitability, growth rate, market share
   - Rank by strategic importance

CRITICAL: Strategic queries need COMPARATIVE DATA for decision-making, not just simple totals!
{'='*70}
"""

        code_generation_prompt = f"""You are an expert pandas code generator for data analysis.

USER QUERY: "{query}"

QUERY ANALYSIS:
{json.dumps(analysis, indent=2)}

{context_section}

{predictive_guidance}

{strategic_guidance}

Generate Python/Pandas code to retrieve the data needed to answer this query.

CRITICAL REQUIREMENTS:
1. Use the DataFrame variable 'df' (already loaded)
2. Generate efficient pandas code
3. Store final result in variable called 'result'
4. Result can be: scalar, dict, DataFrame, or list
5. NO print statements
6. NO comments needed
7. ONLY executable code
8. Use ONLY basic pandas operations: groupby, sum, mean, count, sort_values, head, tail, filter, agg, nunique
9. NO advanced statistics libraries (seasonal_decompose, statsmodels, scipy, etc.)
10. For trends, use groupby with time columns (Year, Quarter, Month)
11. Code must be complete - no truncated lines
12. Each line must be syntactically complete

🚨 CRITICAL DISTINCTION - COUNT vs SUM:
- "How many transactions/rows?" → Use len(df) or df.shape[0] (COUNT rows)
- "What is total sales/revenue?" → Use df['Net_Amount_BDT'].sum() (SUM values)
- "How many products?" → Use df['Product_Name'].nunique() (COUNT unique)
- Keywords: "how many", "count", "number of" = COUNT rows, NOT sum amounts!

BASIC EXAMPLES:

Example 1 - COUNT transactions/rows query (IMPORTANT for "how many"):
```python
result = len(df[df['Year'] == 2024])
```
OR
```python
result = df[df['Year'] == 2024].shape[0]
```

Example 2 - Total sales query:
```python
result = df[df['Year'] == 2024]['Net_Amount_BDT'].sum()
```

Example 3 - Count with filtering (Q3 = Quarter 3):
```python
result = len(df[(df['Year'] == 2024) & (df['Quarter'] == 3)])
```

Example 4 - Comparison query:
```python
data_2024 = df[df['Year'] == 2024]['Net_Amount_BDT'].sum()
data_2023 = df[df['Year'] == 2023]['Net_Amount_BDT'].sum()
result = {{'year_2024': data_2024, 'year_2023': data_2023, 'change_%': ((data_2024/data_2023 - 1) * 100)}}
```

Example 5 - Top items query:
```python
result = df.groupby('Product_Name')['Net_Amount_BDT'].sum().sort_values(ascending=False).head(10).to_dict()
```

Example 6 - Complex analysis:
```python
cement = df[df['Division_Name'] == 'Cement']
quarterly = cement.groupby(['Year', 'Quarter'])['Net_Amount_BDT'].sum().reset_index()
result = quarterly.to_dict('records')
```

Example 7 - Product trend over time:
```python
product_data = df[df['Product_Name'] == 'Chanachur Mix']
monthly_trend = product_data.groupby(['Year', 'Month'])['Net_Amount_BDT'].sum().reset_index()
monthly_trend = monthly_trend.sort_values(['Year', 'Month'])
result = monthly_trend.to_dict('records')
```

Example 8 - Seasonal pattern (by quarter):
```python
product_data = df[df['Product_Name'] == 'Chanachur Mix']
seasonal = product_data.groupby('Quarter')['Net_Amount_BDT'].mean().reset_index()
result = seasonal.to_dict('records')
```

Now generate code for the user query. Return ONLY the Python code in a code block.
Make sure ALL lines are complete with proper closing parentheses and brackets.
"""

        response = self.llm.generate(code_generation_prompt)

        # Extract code
        code = self._extract_code(response)

        return code

    def _generate_simple_code(self, query: str, analysis: Dict, column_info: str, rag_info: str = "") -> str:
        """Generate simpler code as fallback when complex generation fails"""

        # Build context
        context_section = f"{column_info}"
        if rag_info:
            context_section += f"\n\nKNOWLEDGE BASE INFO:\n{rag_info[:500]}..."  # Truncate for simple version

        simple_prompt = f"""Generate SIMPLE pandas code for this query.

USER QUERY: "{query}"

{context_section}

Generate the SIMPLEST possible pandas code. Use basic operations only.

Rules:
- Use df variable
- Store result in 'result' variable
- Use only: filter, groupby, sum, mean, count, sort_values
- NO advanced functions
- Keep it under 5 lines
- Make sure ALL parentheses are closed

Example for product trend:
```python
product_df = df[df['Product_Name'] == 'Product Name']
trend = product_df.groupby(['Year', 'Quarter'])['Net_Amount_BDT'].sum().reset_index()
result = trend.to_dict('records')
```

Generate code now. Return ONLY complete, executable Python code:
"""

        response = self.llm.generate(simple_prompt)
        code = self._extract_code(response)
        return code

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response"""

        # Try to find code block
        code_pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code block, try to find lines that look like code
        lines = response.split('\n')
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                # Check if it looks like Python code
                if any(keyword in stripped for keyword in ['df[', 'df.', '=', 'result', 'groupby', 'sum(', 'mean(']):
                    code_lines.append(stripped)

        if code_lines:
            return '\n'.join(code_lines)

        return ""

    def _validate_code(self, code: str) -> str:
        """Validate code for dangerous operations and syntax - return error message if invalid"""

        # Check if code is empty or too short
        if not code or len(code.strip()) < 5:
            return "Generated code is empty or too short"

        # List of dangerous operations
        dangerous_patterns = [
            ('import os', 'OS operations not allowed'),
            ('import sys', 'System operations not allowed'),
            ('import subprocess', 'Subprocess not allowed'),
            ('__import__', 'Dynamic imports not allowed'),
            ('eval(', 'eval() not allowed'),
            ('exec(', 'exec() not allowed'),
            ('open(', 'File operations not allowed'),
            ('write(', 'Write operations not allowed'),
            ('delete', 'Delete operations not allowed'),
            ('drop(', 'DataFrame drop operations should be avoided'),
            ('to_csv', 'File write operations not allowed'),
            ('to_excel', 'File write operations not allowed'),
            ('to_sql', 'Database operations not allowed'),
            ('seasonal_decompose', 'Advanced statistical functions not available - use basic pandas operations only'),
        ]

        code_lower = code.lower()

        for pattern, error_msg in dangerous_patterns:
            if pattern.lower() in code_lower:
                return error_msg

        # Check for incomplete code (unclosed brackets/parentheses)
        if code.count('(') != code.count(')'):
            return "Incomplete code detected: unmatched parentheses. Code appears to be truncated."

        if code.count('[') != code.count(']'):
            return "Incomplete code detected: unmatched brackets. Code appears to be truncated."

        if code.count('{') != code.count('}'):
            return "Incomplete code detected: unmatched braces. Code appears to be truncated."

        # Check for basic syntax errors
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return f"Syntax error in generated code: {str(e)}"
        except Exception as e:
            return f"Code validation error: {str(e)}"

        return None

    def _execute_pandas_code(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute generated pandas code safely (assumes code is already validated)"""

        try:
            # Create execution context
            exec_globals = {
                'df': df,
                'pd': pd,
                'result': None
            }

            # Execute code
            exec(code, exec_globals)

            result = exec_globals.get('result')

            if result is None:
                return {
                    "success": False,
                    "error": "Code executed but did not assign 'result' variable",
                    "data": None,
                    "code": code
                }

            # Convert result to serializable format
            if isinstance(result, pd.DataFrame):
                result_data = {
                    "type": "dataframe",
                    "data": result.to_dict('records'),
                    "shape": result.shape,
                    "columns": result.columns.tolist()
                }
            elif isinstance(result, pd.Series):
                result_data = {
                    "type": "series",
                    "data": result.to_dict()
                }
            elif isinstance(result, (int, float)):
                result_data = {
                    "type": "scalar",
                    "value": float(result)
                }
            elif isinstance(result, dict):
                result_data = {
                    "type": "dict",
                    "data": result
                }
            elif isinstance(result, list):
                result_data = {
                    "type": "list",
                    "data": result
                }
            else:
                result_data = {
                    "type": "unknown",
                    "data": str(result)
                }

            print(f"✅ Data Retrieved Successfully")
            print(f"   Result Type: {result_data.get('type')}")

            return {
                "success": True,
                "data": result_data,
                "code": code,
                "error": None
            }

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Execution Error: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "traceback": traceback.format_exc(),
                "code": code,
                "data": None
            }
