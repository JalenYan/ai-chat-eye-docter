from openai import OpenAI
import sys

base_url = "https://api.ppinfra.com/v3/openai"
api_key = "sk_rHg6ujMlqiuBxlqaOKX7SYpoO8kS_JsbHsgfmJEfc5U"  # Your API key
model = "deepseek/deepseek-v3/community"

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

def test_chat_completion(prompt="Hi there!", stream=True, max_tokens=1000):
    """
    Test chat completion with the OpenAI client
    
    Args:
        prompt: The user message to send
        stream: Whether to use streaming response
        max_tokens: Maximum number of tokens to generate
    """
    print(f"\nTesting chat completion with prompt: '{prompt}'")
    print(f"Stream: {stream}, Max tokens: {max_tokens}")
    
    # Set response format to text
    response_format = {"type": "text"}
    
    # Create chat completion
    chat_completion_res = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=stream,
        max_tokens=max_tokens,
        response_format=response_format,
        extra_body={}  # You can add any additional parameters here
    )
    
    # Handle response based on stream setting
    print("\nResponse:")
    if stream:
        for chunk in chat_completion_res:
            content = chunk.choices[0].delta.content or ""
            print(content, end="")
    else:
        print(chat_completion_res.choices[0].message.content)
    print("\n")

if __name__ == "__main__":
    # Default values
    prompt = "Hi there!"
    stream = True
    max_tokens = 1000
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    if len(sys.argv) > 2:
        # Parse stream as boolean
        stream_arg = sys.argv[2].lower()
        stream = stream_arg in ("true", "t", "yes", "y", "1")
    if len(sys.argv) > 3:
        max_tokens = int(sys.argv[3])
    
    # Run the test
    test_chat_completion(prompt=prompt, stream=stream, max_tokens=max_tokens) 