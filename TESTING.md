# Testing Guide for the Chat API Service

This document provides instructions on how to test the Chat API Service to verify that it's working properly.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (optional)
- Required dependencies (installed in virtual environment or globally)

## Setting Up for Testing

1. Ensure you have the proper configuration in your `.env` file:

   ```
   # OpenAI API配置
   BASE_URL=https://api.ppinfra.com/v3/openai
   API_KEY=your_api_key_here
   MODEL_ID=deepseek/deepseek-v3/community

   # 服务配置
   PORT=8000
   HOST=0.0.0.0
   LOG_LEVEL=info
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   pip install requests  # For testing
   ```

## Running the Service

### Option 1: Using Python

```bash
python run.py
```

### Option 2: Using Docker

```bash
docker-compose up
```

## Testing Methods

### 1. Basic Health Check

Verify that the service is running by checking the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"ok"}
```

### 2. Testing with API Endpoints

Use the provided test script to test both streaming and non-streaming completions:

```bash
python test_api.py
```

### 3. Testing with OpenAI Client Directly

Use the OpenAI client directly to test the API:

```bash
python test_openai.py
```

### 4. Comprehensive Testing with Custom Parameters

Test with custom prompts, streaming options, and token limits:

```bash
python test_complete.py "Your prompt here" true|false max_tokens
```

Examples:
- `python test_complete.py "Tell me a joke"`
- `python test_complete.py "What's the weather like?" false`
- `python test_complete.py "Write a poem" true 200`

## Troubleshooting

### API Connection Issues

If you encounter API connection issues:

1. Verify your API key is correct
2. Check that the BASE_URL is correctly configured
3. Ensure the model ID is supported by your API provider

### Service Not Starting

1. Check for port conflicts (something might already be using port 8000)
2. Verify that all dependencies are installed
3. Look at the logs for specific error messages

### Streaming Not Working

1. Ensure that your API provider supports streaming responses
2. Verify that the client has proper streaming handling 