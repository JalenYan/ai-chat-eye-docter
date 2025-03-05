"""
Test script for the Eye Doctor Chat API

This script tests the eye doctor chat API by sending a sample request to the API
and printing the response. It can be used to test both standard and streaming modes.
"""

import asyncio
import json
import httpx
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API details 
API_BASE = os.getenv('API_BASE', 'http://localhost:8000')
API_ENDPOINT = f"{API_BASE}/api/eye-doctor/chat"

# Sample request data
sample_request = {
  "disease_name": "糖尿病视网膜病变",
  "disease_category": "视网膜疾病",
  "result": "根据眼部图像分析，患者出现轻度糖尿病视网膜病变，建议定期复查，控制血糖。",
  "remark": "患者需要定期监测血糖和眼部状况",
  "treatment_plan": {
    "treatment_detail": "每天使用人工泪液，避免长时间用眼，定期复查"
  },
  "medications": [
    {
      "medication_name": "人工泪液",
      "dosage": "每次1-2滴",
      "frequency": "每天4次",
      "side_effects": "轻微刺痛感"
    }
  ],
  "previous_conversations": [
    {
      "role": "user",
      "content": "这个病严重吗？"
    },
    {
      "role": "assistant",
      "content": "根据您的眼底检查结果，您目前处于轻度糖尿病视网膜病变阶段。这个阶段并不十分严重，但需要引起重视。糖尿病视网膜病变是一种进行性疾病，如果不加以控制，可能会逐渐发展为更严重的阶段，最终可能导致视力下降甚至失明。因此，定期复查和良好的血糖控制非常重要。"
    }
  ],
  "question": "医生，我爱你，可以做我的男朋友吗？",
  "stream": False
}

async def test_eye_doctor_chat_standard():
    """Test the eye doctor chat API in standard (non-streaming) mode"""
    print("Testing standard (non-streaming) mode...")
    
    # Create request with streaming disabled
    request = sample_request.copy()
    request["stream"] = False
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            API_ENDPOINT,
            json=request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse:")
            print(f"Response ID: {result.get('response_id')}")
            print(f"Content: {result.get('content')}")
            print(f"References: {json.dumps(result.get('references'), indent=2)}")
            print(f"Created at: {result.get('created_at')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

async def test_eye_doctor_chat_streaming():
    """Test the eye doctor chat API in streaming mode"""
    print("\nTesting streaming mode...")
    
    # Create request with streaming enabled
    request = sample_request.copy()
    request["stream"] = True
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream('POST', API_ENDPOINT, json=request) as response:
            if response.status_code == 200:
                print("\nStreaming response:")
                complete_content = ""
                
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("content", "")
                            complete_content += content
                            print(content, end="", flush=True)
                            
                            # Check if this is the last chunk
                            if chunk.get("is_complete"):
                                print("\n\nFinal metadata:")
                                print(f"Response ID: {chunk.get('response_id')}")
                                print(f"References: {json.dumps(chunk.get('references'), indent=2)}")
                                print(f"Created at: {chunk.get('created_at')}")
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {data}")
                
                print("\n\nComplete content:")
                print(complete_content)
            else:
                print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    import sys
    
    # Check if mode is specified in command line arguments
    mode = "both"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    # Run the test(s)
    loop = asyncio.get_event_loop()
    if mode in ["streaming", "both"]:
        loop.run_until_complete(test_eye_doctor_chat_streaming()) 
    if mode in ["standard", "both"]:
        loop.run_until_complete(test_eye_doctor_chat_standard())