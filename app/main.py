import logging
import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from .models.chat import ChatCompletionRequest, ChatCompletionResponse, ErrorResponse
from .services.llm_service import llm_service
from .utils.config import settings

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

# If this file is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    ) 