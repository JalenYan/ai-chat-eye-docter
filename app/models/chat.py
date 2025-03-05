from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message model"""
    role: Literal["system", "user", "assistant"] = Field(...)
    content: str = Field(...)

class ChatCompletionRequest(BaseModel):
    """Chat completion request model"""
    messages: List[Message] = Field(..., description="Message history")
    model: Optional[str] = Field(None, description="Model to use")
    temperature: Optional[float] = Field(0.7, description="Randomness of generation", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to use streaming response")

class TokenUsage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    """Chat completion response model"""
    message: Message
    usage: TokenUsage

class ErrorResponse(BaseModel):
    """Error response model"""
    error: bool = True
    message: str
    detail: Optional[Dict[str, Any]] = None 