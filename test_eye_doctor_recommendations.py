"""
Test script for the Eye Doctor Recommendations API

This script tests the eye doctor recommendations API by sending a sample request
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
API_ENDPOINT = f"{API_BASE}/api/eye-doctor/recommendations"

# Sample request data
sample_request = {
    "disease_name": "糖尿病视网膜病变",
    "disease_category": "视网膜疾病",
    "result": "根据眼部图像分析，患者出现轻度糖尿病视网膜病变，建议定期复查，控制血糖。",
    "patient_info": {   
        "name": "张三",
        "sex": "男",
        "age": 21
    },
    "stream": False
}

async def test_recommendations_standard():
    """Test the recommendations API in standard (non-streaming) mode"""
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
            print("\nRecommended Medications:")
            for med in result.get('medications', []):
                print(f"\n- {med.get('medication_name')}:")
                print(f"  Dosage: {med.get('dosage')}")
                print(f"  Frequency: {med.get('frequency')}")
                print(f"  Side Effects: {med.get('side_effects')}")
            
            print("\nTreatment Plan:")
            treatment = result.get('treatment_plan', {})
            print(f"Type: {treatment.get('treatment_type')}")
            print(f"Details: {treatment.get('treatment_detail')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

async def test_recommendations_streaming():
    """Test the recommendations API in streaming mode"""
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
                            content = json.loads(data)
                            if isinstance(content, dict) and 'error' in content:
                                print(f"\nError in stream: {content['error']}")
                            else:
                                print(data, end="", flush=True)
                                complete_content += data
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {data}")
                
                print("\n\nComplete content:")
                try:
                    recommendations = json.loads(complete_content)
                    print("\nRecommended Medications:")
                    for med in recommendations.get('medications', []):
                        print(f"\n- {med.get('medication_name')}:")
                        print(f"  Dosage: {med.get('dosage')}")
                        print(f"  Frequency: {med.get('frequency')}")
                        print(f"  Side Effects: {med.get('side_effects')}")
                    
                    print("\nTreatment Plan:")
                    treatment = recommendations.get('treatment_plan', {})
                    print(f"Type: {treatment.get('treatment_type')}")
                    print(f"Details: {treatment.get('treatment_detail')}")
                except json.JSONDecodeError:
                    print("Error: Could not parse complete content as JSON")
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
        loop.run_until_complete(test_recommendations_streaming())
    if mode in ["standard", "both"]:
        loop.run_until_complete(test_recommendations_standard()) 