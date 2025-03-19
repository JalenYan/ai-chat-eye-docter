from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

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

class PatientInfo(BaseModel):
    """Patient information model"""
    name: str = Field(..., description="Patient's name")
    sex: str = Field(..., description="Patient's sex")
    age: int = Field(..., description="Patient's age")

class Medication(BaseModel):
    """Medication recommendation model"""
    medication_name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Dosage instructions")
    frequency: str = Field(..., description="Frequency of use")
    side_effects: Optional[str] = Field(None, description="Potential side effects")

class TreatmentPlan(BaseModel):
    """Treatment plan model"""
    treatment_type: str = Field(..., description="Type of treatment")
    treatment_detail: str = Field(..., description="Detailed treatment instructions")

class AIRecommendationRequest(BaseModel):
    """AI recommendation request model"""
    disease_name: str = Field(..., description="Name of the diagnosed disease")
    disease_category: str = Field(..., description="Category of the disease")
    result: str = Field(..., description="Examination result")
    patient_info: PatientInfo = Field(..., description="Patient information")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")

class AIRecommendationResponse(BaseModel):
    """AI recommendation response model"""
    medications: List[Medication] = Field(..., description="List of recommended medications")
    treatment_plan: TreatmentPlan = Field(..., description="Recommended treatment plan")