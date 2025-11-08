"""Request models for API endpoints"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    query: str = Field(
        ...,
        description="User query or question",
        min_length=1,
        max_length=500,
        examples=["What was total sales in 2024?"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What were the top 5 products by revenue in 2024?"
            }
        }
