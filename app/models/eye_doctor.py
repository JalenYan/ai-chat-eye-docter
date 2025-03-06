from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Eye Doctor chat model classes
class EyeDoctorRequest(BaseModel):
    """Eye doctor chat request model"""
    disease_name: str = Field(..., description="Name of the diagnosed disease")
    disease_category: str = Field(..., description="Category of the disease")
    result: str = Field(..., description="Examination result")
    remark: Optional[str] = Field(None, description="Additional remarks")
    treatment_plan: Optional[Dict[str, Any]] = Field(None, description="Treatment plan details")
    medications: Optional[list] = Field(None, description="List of medications")
    previous_conversations: Optional[list] = Field(None, description="Previous conversation history")
    question: str = Field(..., description="Patient's question")
    model: Optional[str] = Field(None, description="LLM model to use")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")

class EyeDoctorResponse(BaseModel):
    """Eye doctor chat response model"""
    response_id: str = Field(..., description="Unique response ID")
    content: str = Field(..., description="Response content")
    references: Optional[list] = Field(None, description="References used")
    created_at: str = Field(..., description="Response creation timestamp")