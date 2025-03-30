from typing import List, Dict, Any, Optional
import logging
import httpx
import json
from openai import AsyncOpenAI, APIError, RateLimitError
from ..utils.config import settings
from ..models.chat import Message, TokenUsage
from ..utils.prompts import construct_prompt, construct_recommendation_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").propagate = False
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
    
    async def get_eye_doctor_completion(
        self,
        request_data: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Get specialized eye doctor chat completion response
        
        Args:
            request_data: Dictionary containing patient information and question
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
            # Construct specialized prompt using prompt engineering
            system_prompt, user_message = construct_prompt(request_data)
            
            # Create messages list
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_message)
            ]
            
            # Add previous conversation context if available
            previous_conversations = request_data.get('previous_conversations', [])
            if previous_conversations:
                # Reset messages to just include system prompt
                messages = [Message(role="system", content=system_prompt)]
                
                # Add each message from previous conversations
                for msg in previous_conversations:
                    role = msg.get('role')
                    content = msg.get('content')
                    if role in ['user', 'assistant'] and content:
                        messages.append(Message(role=role, content=content))
                
                # Add the current user query at the end
                messages.append(Message(role="user", content=user_message))
            
            # Call the standard chat completion method
            return await self.get_chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
        except Exception as e:
            logger.error(f"Error in eye doctor completion: {str(e)}")
            raise Exception(f"Error processing eye doctor request: {str(e)}")

    async def get_eye_doctor_recommendations(
        self,
        request_data: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Get AI-generated medication and treatment recommendations
        
        Args:
            request_data: Dictionary containing patient and disease information
            stream: Whether to use streaming response, defaults to False
            
        Returns:
            Dictionary containing recommended medications and treatment plan
            
        Raises:
            Exception: Various exceptions related to API errors
        """
        try:
            # Construct specialized prompt for recommendations
            system_prompt, user_message = construct_recommendation_prompt(request_data)
            
            # Create messages list
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_message)
            ]
            
            # Call the chat completion method with stricter parameters
            result = await self.get_chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent output
                stream=stream,
                max_tokens=1000  # Limit response length
            )
            
            if stream:
                return {"stream": result["stream"]}
            
            # Parse and validate the response content
            try:
                content = result["message"].content.strip()
                
                # Try to find JSON content if there's any extra text
                if content.find('{') != 0:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start >= 0 and end > start:
                        content = content[start:end]
                
                recommendations = json.loads(content)
                
                # Validate the structure
                if not isinstance(recommendations, dict):
                    raise ValueError("Response is not a JSON object")
                
                if "medications" not in recommendations or "treatment_plan" not in recommendations:
                    raise ValueError("Missing required fields: medications or treatment_plan")
                
                if not isinstance(recommendations["medications"], list):
                    raise ValueError("medications must be an array")
                
                if not isinstance(recommendations["treatment_plan"], dict):
                    raise ValueError("treatment_plan must be an object")
                
                # Validate medications
                for med in recommendations["medications"]:
                    required_fields = ["medication_name", "dosage", "frequency", "side_effects"]
                    missing_fields = [f for f in required_fields if f not in med]
                    if missing_fields:
                        raise ValueError(f"Medication missing required fields: {', '.join(missing_fields)}")
                
                # Validate treatment plan
                required_fields = ["treatment_type", "treatment_detail"]
                missing_fields = [f for f in required_fields if f not in recommendations["treatment_plan"]]
                if missing_fields:
                    raise ValueError(f"Treatment plan missing required fields: {', '.join(missing_fields)}")
                
                return {"recommendations": recommendations}
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing recommendations JSON: {str(e)}")
                logger.error(f"Raw content: {result['message'].content}")
                raise Exception("Invalid JSON format in model response")
            except ValueError as e:
                logger.error(f"Invalid recommendations format: {str(e)}")
                logger.error(f"Parsed content: {recommendations}")
                raise Exception(f"Invalid recommendations format: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in eye doctor recommendations: {str(e)}")
            raise Exception(f"Error generating recommendations: {str(e)}")

# Create service instance
llm_service = LLMService() 