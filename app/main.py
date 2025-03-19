import logging
import time
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from .models.chat import ChatCompletionRequest, ChatCompletionResponse, ErrorResponse, Message
from .models.eye_doctor import (
    EyeDoctorRequest, 
    EyeDoctorResponse, 
    AIRecommendationRequest, 
    AIRecommendationResponse
)
from .services.llm_service import llm_service
from .utils.config import settings
from .utils.register2nacos_config import init_app
# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Define application lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Starting up ChatGPT API Service")
    yield
    # Shutdown event
    logger.info("Shutting down ChatGPT API Service")

# Create FastAPI application
app = FastAPI(
    title="ChatGPT API Service",
    description="A stateless API service for interacting with ChatGPT",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production environment, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize Nacos configuration
init_app()
# Add request processing middleware for logging and performance monitoring
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request path: {request.url.path} - Processed in {process_time:.4f} seconds")
    return response

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="An unexpected error occurred",
            detail={"error": str(exc)}
        ).model_dump(),
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Chat endpoint
@app.post("/api/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    Process chat completion requests
    
    Receives a request with message history, calls the OpenAI API, and returns the AI-generated response
    """
    try:
        result = await llm_service.get_chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # Handle streaming response
        if request.stream and result.get("stream"):
            async def generate():
                try:
                    async for chunk in result["stream"]:
                        content = chunk.choices[0].delta.content or ""
                        yield f"data: {content}\n\n"
                except Exception as e:
                    logger.error(f"Error in streaming: {str(e)}")
                    yield f"data: [ERROR] {str(e)}\n\n"
                finally:
                    yield "data: [DONE]\n\n"
                    
            return StreamingResponse(generate(), media_type="text/event-stream")
            
        # Handle regular response
        return result
        
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Eye Doctor chat endpoint
@app.post("/api/eye-doctor/chat", response_model=EyeDoctorResponse)
async def eye_doctor_chat(request: EyeDoctorRequest):
    """
    Process eye doctor chat requests
    
    Receives patient data and question, constructs specialized prompts,
    calls the LLM, and returns a formatted response
    """
    try:
        import uuid
        from datetime import datetime, timezone
        
        # Generate a unique response ID
        response_id = str(uuid.uuid4())
        
        # Convert request to dictionary
        request_data = request.model_dump()
        
        # Call the eye doctor completion service
        result = await llm_service.get_eye_doctor_completion(
            request_data=request_data,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # Handle streaming response
        if request.stream and result.get("stream"):
            async def generate():
                try:
                    chunk_id = 0
                    complete_content = ""
                    
                    async for chunk in result["stream"]:
                        chunk_id += 1
                        content = chunk.choices[0].delta.content or ""
                        complete_content += content
                        
                        # Check if this is the last chunk
                        is_complete = chunk.choices[0].finish_reason is not None
                        
                        # Create response chunk
                        response_chunk = {
                            "response_id": response_id,
                            "chunk_id": chunk_id,
                            "content": content,
                            "is_complete": is_complete
                        }
                        
                        # For the last chunk, include references and timestamp
                        if is_complete:
                            # Extract references if they exist
                            references = []
                            # Simple reference extraction logic - could be more sophisticated
                            if "参考资料" in complete_content:
                                ref_section = complete_content.split("参考资料")[-1]
                                ref_lines = [line.strip() for line in ref_section.split("\n") if line.strip()]
                                for line in ref_lines:
                                    parts = line.split(",")
                                    if len(parts) >= 2:
                                        ref = {"title": parts[0].strip("- ")}
                                        if len(parts) > 1:
                                            ref["source"] = parts[1].strip()
                                        if len(parts) > 2:
                                            try:
                                                ref["year"] = int(parts[2].strip())
                                            except ValueError:
                                                pass
                                        references.append(ref)
                            
                            response_chunk["references"] = references
                            response_chunk["created_at"] = datetime.now(timezone.utc).isoformat()
                            
                        yield f"data: {json.dumps(response_chunk)}\n\n"
                        
                except Exception as e:
                    logger.error(f"Error in streaming: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                finally:
                    yield "data: [DONE]\n\n"
                    
            return StreamingResponse(generate(), media_type="text/event-stream")
            
        # Handle regular response
        if result.get("message"):
            # Extract content from message
            content = result["message"].content
            
            # Extract references if they exist
            references = []
            # Simple reference extraction logic - could be more sophisticated
            if "参考资料" in content:
                ref_section = content.split("参考资料")[-1]
                ref_lines = [line.strip() for line in ref_section.split("\n") if line.strip()]
                for line in ref_lines:
                    parts = line.split(",")
                    if len(parts) >= 2:
                        ref = {"title": parts[0].strip("- ")}
                        if len(parts) > 1:
                            ref["source"] = parts[1].strip()
                        if len(parts) > 2:
                            try:
                                ref["year"] = int(parts[2].strip())
                            except ValueError:
                                pass
                        references.append(ref)
            
            # Create response
            response = {
                "response_id": response_id,
                "content": content,
                "references": references,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return response
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response"
        )
        
    except Exception as e:
        logger.error(f"Error in eye doctor chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# AI recommendation endpoint
@app.post("/api/eye-doctor/recommendations", response_model=AIRecommendationResponse)
async def get_ai_recommendations(request: AIRecommendationRequest):
    """
    Get AI-generated medication and treatment recommendations
    
    Receives patient data and diagnosis information, analyzes it using the LLM,
    and returns recommended medications and treatment plan
    """
    try:
        # Convert request to dictionary
        request_data = request.model_dump()
        
        # Call the eye doctor recommendation service
        result = await llm_service.get_eye_doctor_recommendations(
            request_data=request_data,
            stream=request.stream
        )
        
        # Handle streaming response
        if request.stream and result.get("stream"):
            async def generate():
                try:
                    complete_content = ""
                    
                    async for chunk in result["stream"]:
                        content = chunk.choices[0].delta.content or ""
                        complete_content += content
                        
                        # Check if this is the last chunk
                        is_complete = chunk.choices[0].finish_reason is not None
                        
                        if is_complete:
                            try:
                                # Parse the complete content as JSON
                                recommendations = json.loads(complete_content)
                                yield f"data: {json.dumps(recommendations)}\n\n"
                            except json.JSONDecodeError as e:
                                logger.error(f"Error parsing recommendations JSON: {str(e)}")
                                yield f"data: {json.dumps({'error': 'Invalid recommendations format'})}\n\n"
                        else:
                            yield f"data: {content}\n\n"
                        
                except Exception as e:
                    logger.error(f"Error in streaming: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                finally:
                    yield "data: [DONE]\n\n"
                    
            return StreamingResponse(generate(), media_type="text/event-stream")
            
        # Handle regular response
        if result.get("recommendations"):
            return result["recommendations"]
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )
        
    except Exception as e:
        logger.error(f"Error in AI recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# If this file is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
