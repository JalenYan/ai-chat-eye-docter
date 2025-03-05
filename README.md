# ChatGPT API Service

一个无状态的FastAPI服务，用于与ChatGPT进行交互。该服务设计为由Java后端调用，Java后端负责管理聊天历史和用户会话。

## 功能特点

- 基于FastAPI构建的高性能异步API
- 与OpenAI GPT API的集成
- 无状态设计，易于扩展和部署
- 详细的错误处理和日志记录
- 支持自定义模型和生成参数

## 安装

1. 克隆仓库:

```bash
git clone <repository-url>
cd chatgpt-service
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 创建 `.env` 文件:

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入您的OpenAI API密钥和其他配置。

## 配置

在 `.env` 文件中配置以下项:

- `API_KEY`: 您的OpenAI API密钥
- `MODEL_ID`: 默认使用的模型 (默认: "gpt-3.5-turbo")
- `PORT`: 服务运行的端口 (默认: 8000)
- `HOST`: 服务监听的主机 (默认: "0.0.0.0")
- `LOG_LEVEL`: 日志级别 (默认: "info")

## 运行服务

```bash
python run.py
```

或者使用uvicorn直接运行:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

服务启动后，可以访问以下URL查看API文档:

- Swagger UI: `http://<host>:<port>/docs`
- ReDoc: `http://<host>:<port>/redoc`

## API 端点

### 健康检查

```
GET /health
```

用于检查服务是否正常运行。

### 聊天完成

```
POST /api/chat/completions
```

发送消息并获取AI回复。

请求示例:

```json
{
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么我可以帮助你的？"},
    {"role": "user", "content": "介绍一下Python"}
  ],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 500
}
```

响应示例:

```json
{
  "message": {
    "role": "assistant",
    "content": "Python是一种高级编程语言..."
  },
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 120,
    "total_tokens": 170
  }
}
```

## 与Java后端集成

示例Java代码:

```java
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestTemplate;

// ...

public ChatResponse sendChatRequest(List<Message> messages) {
    String url = "http://chatgpt-service:8000/api/chat/completions";
    
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    
    Map<String, Object> requestBody = new HashMap<>();
    requestBody.put("messages", messages);
    requestBody.put("model", "gpt-3.5-turbo");
    requestBody.put("temperature", 0.7);
    
    HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
    
    RestTemplate restTemplate = new RestTemplate();
    return restTemplate.postForObject(url, request, ChatResponse.class);
}
```

## 错误处理

服务会返回适当的HTTP状态码和详细的错误消息，以帮助调试和处理错误情况。常见错误包括:

- 400: 请求格式错误
- 500: 服务器内部错误，包括OpenAI API错误

## 许可证

[MIT License](LICENSE)

## Docker Development Environment

This project includes Docker configuration for easy development setup.

### Prerequisites

- Docker
- Docker Compose

### Getting Started with Docker

1. Copy the example environment file and configure it:
   ```
   cp .env.example .env
   ```
   Then edit `.env` to add your API keys and configuration.

2. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

3. The API will be available at http://localhost:8000 (or the port you configured in .env)

### Development with Docker

- The code is mounted as a volume, so changes you make to the code will be reflected immediately thanks to the `--reload` flag.
- To run commands inside the container:
  ```
  docker-compose exec api python -c "import sys; print(sys.version)"
  ```
- To stop the containers:
  ```
  docker-compose down
  ``` 