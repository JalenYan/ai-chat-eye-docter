# ChatGPT API Service

一个无状态的FastAPI服务，用于与ChatGPT进行交互。该服务设计为由Java后端调用，Java后端负责(通过配置openfeign远程调用fastApi接口)管理聊天历史和用户会话。

## 功能特点

- 基于FastAPI构建的高性能异步API
- 与OpenAI GPT API的集成
- 无状态设计，易于扩展和部署
- 详细的错误处理和日志记录
- 支持自定义模型和生成参数
- 眼科医生智能问答功能，处理眼科相关的咨询

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
- `API_BASE`: 用于眼科医生API测试的基础URL (默认: "http://localhost:8000")

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

### 聊天补全

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

### 眼科医生智能问答

```
POST /api/eye-doctor/chat
```

发送眼科相关咨询并获取专业回复。此端点专为眼科咨询设计，能处理包含疾病信息、治疗方案和患者提问的复杂请求。

请求示例:

```json
{
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
  "question": "我需要注意些什么？",
  "stream": false
}
```

响应示例:

```json
{
  "response_id": "resp_123456789",
  "content": "作为您的眼科医生，我建议您需要注意以下几点：\n\n1. 控制血糖：糖尿病视网膜病变与血糖控制密切相关，请遵医嘱控制血糖水平。\n\n2. 定期复查：即使没有明显症状，也需要每3-6个月进行一次眼底检查，以监测病情变化。\n\n3. 用药规范：按照处方正确使用人工泪液，每天4次，每次1-2滴。\n\n4. 生活习惯：避免长时间用眼，保持充足睡眠，戒烟限酒。\n\n5. 饮食调整：增加绿叶蔬菜和富含抗氧化物质的食物摄入。\n\n如有任何不适，如视力突然下降、眼前黑影增多等症状，请立即就医。",
  "references": [
    {
      "title": "糖尿病视网膜病变患者指南",
      "url": "https://example.com/guide"
    }
  ],
  "created_at": "2023-06-01T12:34:56Z"
}
```

支持流式响应模式，只需将请求中的 `stream` 参数设置为 `true`。

## 测试

详细的测试指南请参阅 [TESTING.md](TESTING.md) 文件。支持以下测试方法：

- 基本健康检查
- 标准API端点测试
- OpenAI客户端测试
- 自定义参数测试
- 眼科医生问答API测试（支持标准和流式模式）

运行眼科医生问答测试：

```bash
python test_eye_doctor.py [mode]
```

其中 `mode` 可选值为：`standard`、`streaming` 或 `both`。

## 与Java后端集成

### 标准聊天补全集成

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
    requestBody.put("model", "deepseek/deepseek-v3/community");
    requestBody.put("temperature", 0.7);
    
    HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
    
    RestTemplate restTemplate = new RestTemplate();
    return restTemplate.postForObject(url, request, ChatResponse.class);
}
```

### 眼科医生问答集成

示例Java代码:

```java
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestTemplate;
import java.util.*;

// 眼科医生问答请求
public EyeDoctorResponse sendEyeDoctorRequest(
        String diseaseName, 
        String diseaseCategory, 
        String result, 
        String remark, 
        Map<String, String> treatmentPlan,
        List<Map<String, String>> medications,
        List<Map<String, String>> previousConversations,
        String question,
        boolean stream) {
    
    String url = "http://chatgpt-service:8000/api/eye-doctor/chat";
    
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    
    Map<String, Object> requestBody = new HashMap<>();
    requestBody.put("disease_name", diseaseName);
    requestBody.put("disease_category", diseaseCategory);
    requestBody.put("result", result);
    requestBody.put("remark", remark);
    requestBody.put("treatment_plan", treatmentPlan);
    requestBody.put("medications", medications);
    requestBody.put("previous_conversations", previousConversations);
    requestBody.put("question", question);
    requestBody.put("stream", stream);
    
    HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
    
    RestTemplate restTemplate = new RestTemplate();
    
    // 非流式响应处理
    if (!stream) {
        return restTemplate.postForObject(url, request, EyeDoctorResponse.class);
    } else {
        // 流式响应处理需要使用不同的方法，例如使用WebClient
        // 这里仅作示例，实际实现可能需要根据项目需求调整
        System.out.println("流式响应需要使用异步HTTP客户端处理");
        return null;
    }
}

// 使用示例
public void exampleUsage() {
    // 构建治疗计划
    Map<String, String> treatmentPlan = new HashMap<>();
    treatmentPlan.put("treatment_detail", "每天使用人工泪液，避免长时间用眼，定期复查");
    
    // 构建药物信息
    List<Map<String, String>> medications = new ArrayList<>();
    Map<String, String> medication = new HashMap<>();
    medication.put("medication_name", "人工泪液");
    medication.put("dosage", "每次1-2滴");
    medication.put("frequency", "每天4次");
    medication.put("side_effects", "轻微刺痛感");
    medications.add(medication);
    
    // 构建历史对话
    List<Map<String, String>> previousConversations = new ArrayList<>();
    Map<String, String> userMessage = new HashMap<>();
    userMessage.put("role", "user");
    userMessage.put("content", "这个病严重吗？");
    
    Map<String, String> assistantMessage = new HashMap<>();
    assistantMessage.put("role", "assistant");
    assistantMessage.put("content", "根据您的眼底检查结果，您目前处于轻度糖尿病视网膜病变阶段。这个阶段并不十分严重，但需要引起重视。");
    
    previousConversations.add(userMessage);
    previousConversations.add(assistantMessage);
    
    // 发送请求
    EyeDoctorResponse response = sendEyeDoctorRequest(
        "糖尿病视网膜病变",
        "视网膜疾病",
        "根据眼部图像分析，患者出现轻度糖尿病视网膜病变，建议定期复查，控制血糖。",
        "患者需要定期监测血糖和眼部状况",
        treatmentPlan,
        medications,
        previousConversations,
        "我需要注意些什么？",
        false
    );
    
    // 处理响应
    System.out.println("响应ID: " + response.getResponseId());
    System.out.println("内容: " + response.getContent());
    System.out.println("参考资料: " + response.getReferences());
    System.out.println("创建时间: " + response.getCreatedAt());
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
