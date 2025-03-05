import requests
import json
import sys

# API configuration
api_url = "http://localhost:8000/api/chat/completions"
headers = {
    "Content-Type": "application/json"
}

def test_chat_completion(stream=False):
    """Test the chat completion API"""
    print(f"\nTesting {'streaming' if stream else 'regular'} chat completion...")
    
    # Create request payload
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "model": "deepseek/deepseek-v3/community",
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": stream
    }
    
    try:
        if stream:
            # For streaming, we need to use a different approach
            response = requests.post(api_url, headers=headers, json=payload, stream=True)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return
                
            print("Response:")
            for line in response.iter_lines():
                if line:
                    # Remove the "data: " prefix and print the content
                    content = line.decode('utf-8').replace('data: ', '')
                    if content == "[DONE]":
                        break
                    print(content, end="")
            print("\n")
        else:
            # For regular requests
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return
                
            result = response.json()
            print("Response:")
            print(result["message"]["content"])
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test both streaming and non-streaming
    test_mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if test_mode in ["stream", "both"]:
        test_chat_completion(stream=True)
        
    if test_mode in ["regular", "both"]:
        test_chat_completion(stream=False)