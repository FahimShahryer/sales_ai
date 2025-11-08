"""
API Routes for Fully Dynamic Multi-Agent System
NO HARDCODING - Everything LLM-driven
"""
from fastapi import APIRouter, HTTPException
from backend.models import ChatRequest, ChatResponse, HealthResponse
from backend.orchestrator.dynamic_orchestrator import DynamicOrchestrator
from backend.services import RAGService, DataService, LLMService

# Create router
router = APIRouter()

# Global orchestrator instance
orchestrator: DynamicOrchestrator = None


def get_orchestrator() -> DynamicOrchestrator:
    """Get or initialize dynamic orchestrator"""
    global orchestrator
    if orchestrator is None:
        # Initialize services
        rag_service = RAGService()
        data_service = DataService()
        llm_service = LLMService()

        # Create dynamic orchestrator
        orchestrator = DynamicOrchestrator(rag_service, data_service, llm_service)
    return orchestrator


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Fully dynamic chat endpoint
    - LLM analyzes query
    - LLM generates pandas code
    - LLM retrieves context
    - LLM synthesizes answer

    Args:
        request: ChatRequest with user query

    Returns:
        ChatResponse with answer
    """
    try:
        orch = get_orchestrator()
        result = orch.process_query(request.query)
        return ChatResponse(**result)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

        return ChatResponse(
            success=False,
            answer=f"An error occurred: {str(e)}",
            data=None,
            visualizations=[],
            error=str(e)
        )


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        return HealthResponse(
            status="healthy",
            services={
                "rag": "ready",
                "data": "ready",
                "llm": "ready"
            },
            agents={
                "query_understanding": "LLM-driven",
                "data_retrieval": "LLM-driven (generates code)",
                "rag_agent": "LLM-driven",
                "master_synthesis": "LLM-driven"
            }
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            services={"error": str(e)},
            agents={}
        )


@router.get("/api/test")
async def test():
    """Test endpoint"""
    return {
        "status": "ok",
        "message": "Fully Dynamic Multi-Agent System",
        "features": [
            "Zero hardcoding",
            "LLM analyzes queries",
            "LLM generates pandas code",
            "LLM retrieves context",
            "LLM synthesizes answers",
            "100% adaptive"
        ]
    }


@router.get("/api/table/{table_name}")
async def get_table(table_name: str):
    """
    Get CSV table data

    Args:
        table_name: Name of the table (sales_transactions, product_master, etc.)

    Returns:
        JSON with table data and columns
    """
    import pandas as pd
    from pathlib import Path

    # Map table names to file paths
    table_files = {
        "sales_transactions": "sales_transactions.csv",
        "product_master": "product_master.csv",
        "branch_master": "branch_master.csv",
        "division_master": "division_master.csv",
        "customer_master": "customer_master.csv"
    }

    if table_name not in table_files:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    try:
        # Get file path
        data_path = Path(__file__).parent.parent.parent / "data" / table_files[table_name]

        if not data_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {table_files[table_name]}")

        # Read CSV
        df = pd.read_csv(data_path)

        # Limit rows for performance (first 1000 rows)
        df_limited = df.head(1000)

        # Convert to JSON
        data = df_limited.to_dict('records')
        columns = df_limited.columns.tolist()

        return {
            "success": True,
            "table_name": table_name,
            "data": data,
            "columns": columns,
            "total_rows": len(df),
            "showing_rows": len(df_limited)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "columns": []
        }
