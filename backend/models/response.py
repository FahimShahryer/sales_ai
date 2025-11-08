"""Response models for API endpoints"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class VisualizationData(BaseModel):
    """Visualization data for charts"""
    type: str = Field(description="Chart type: bar, line, pie, table")
    data: Dict[str, Any] = Field(description="Chart data with labels and datasets")
    title: Optional[str] = Field(None, description="Chart title")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    success: bool = Field(description="Whether the query was processed successfully")
    answer: str = Field(description="Natural language answer")
    data: Optional[Dict[str, Any]] = Field(None, description="Raw data result")
    visualizations: List[VisualizationData] = Field(
        default=[],
        description="List of visualizations to render"
    )
    agent: Optional[str] = Field(None, description="Agent that processed the query")
    query_type: Optional[str] = Field(None, description="Type of analytics performed")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Total sales in 2024 were ৳1.17 billion, representing a 24% increase from 2023.",
                "data": {
                    "type": "scalar",
                    "value": 1173413000.0
                },
                "visualizations": [
                    {
                        "type": "bar",
                        "data": {
                            "labels": ["2023", "2024"],
                            "datasets": [{
                                "label": "Sales (BDT)",
                                "data": [947060800, 1173413000]
                            }]
                        }
                    }
                ],
                "agent": "Data Analyst Agent",
                "query_type": "Descriptive Analytics"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""

    status: str = Field(description="System status")
    services: Dict[str, str] = Field(description="Status of each service")
    agents: Dict[str, str] = Field(description="Status of each agent")
    data_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of loaded data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "rag": "ready",
                    "data": "ready",
                    "llm": "ready"
                },
                "agents": {
                    "data_analyst": "ready",
                    "detective": "ready",
                    "forecaster": "ready",
                    "strategist": "ready"
                },
                "data_summary": {
                    "total_transactions": 161554,
                    "total_revenue": 3202234050.0
                }
            }
        }
