from openai import OpenAI

# API configuration
base_url = "https://api.ppinfra.com/v3/openai"
api_key = "sk_rHg6ujMlqiuBxlqaOKX7SYpoO8kS_JsbHsgfmJEfc5U"  # Your actual API key
model = "deepseek/deepseek-v3/community"

# Initialize client
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

def test_completion(stream=False):
    """Test completion with the OpenAI client directly"""
    print(f"\nTesting {'streaming' if stream else 'regular'} completion using OpenAI client directly...")
    
    max_tokens = 100
    
    # Create chat completion
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about AI.",
            }
        ],
        stream=stream,
        max_tokens=max_tokens
    )
    
    # Handle response based on stream setting
    if stream:
        # Process streaming response
        print("Response:")
        for chunk in chat_completion:
            # Print the content of each chunk
            content = chunk.choices[0].delta.content or ""
            print(content, end="")
        print("\n")
    else:
        # Process regular response
        print("Response:")
        print(chat_completion.choices[0].message.content)

if __name__ == "__main__":
    print("Testing the OpenAI client directly")
    
    # Test both streaming and regular responses
    test_completion(stream=True)
    test_completion(stream=False) 