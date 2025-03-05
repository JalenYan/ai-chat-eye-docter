from typing import List, Dict, Any, Optional
import logging
import httpx
from openai import AsyncOpenAI, APIError, RateLimitError
from ..utils.config import settings
from ..models.chat import Message, TokenUsage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """LLM service for interacting with the OpenAI API"""
    
    def __init__(self):
        """Initialize the LLM service with OpenAI client and default model"""
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base or None  # Use base_url if provided
        )
        self.default_model = settings.openai_default_model
        
    async def get_chat_completion(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Get chat completion response from OpenAI API
        
        Args:
            messages: List of conversation messages
            model: Model name to use, defaults to configured model
            temperature: Controls randomness in generation, defaults to 0.7
            max_tokens: Maximum number of tokens to generate, defaults to None
            stream: Whether to use streaming response, defaults to False
            
        Returns:
            Dictionary containing generated message and token usage statistics
            
        Raises:
            Exception: Various exceptions related to API errors
        """
        try:
            # Prepare request parameters
            model_to_use = model or self.default_model
            messages_dict = [msg.model_dump() for msg in messages]
            
            request_params = {
                "model": model_to_use,
                "messages": messages_dict,
                "temperature": temperature,
            }
            
            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            
            # Handle streaming response
            if stream:
                request_params["stream"] = True
                stream_response = await self.client.chat.completions.create(**request_params)
                return {
                    "stream": stream_response,
                    "message": None,
                    "usage": None
                }
            
            # For non-streaming response
            response = await self.client.chat.completions.create(**request_params)
            
            # Process response
            assistant_message = Message(
                role="assistant",
                content=response.choices[0].message.content
            )
            
            # Extract token usage statistics
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            return {
                "message": assistant_message,
                "usage": usage
            }
            
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
            raise Exception("Rate limit exceeded, please try again later")
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"API error: {str(e)}")
        except httpx.ReadTimeout:
            logger.error("Request to OpenAI API timed out")
            raise Exception("Request timed out, please try again")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
            raise Exception(f"Error processing request: {str(e)}")

# Create service instance
llm_service = LLMService() 