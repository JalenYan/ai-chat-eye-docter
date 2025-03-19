# 基于提示词工程的AI推荐系统需求

## 定义：
1. 系统：本python项目
2. 服务器：Java服务器

## 背景：
眼科疾病诊断后的用药和治疗建议是患者最关心的问题之一。为了提供更加规范和个性化的建议，需要开发一个基于AI的推荐系统，根据患者的诊断结果和个人信息，生成合适的用药方案和治疗建议。

## 概要：
Java服务器接收到客户端的诊断报告后，请求本系统生成用药和治疗建议。本系统调用模型API，基于提示词工程给出智能推荐，并以结构化的JSON格式返回给Java服务器。

## 系统输入：
```json
{
  "disease_name": "糖尿病视网膜病变",
  "disease_category": "视网膜疾病",
  "result": "根据眼部图像分析，患者出现轻度糖尿病视网膜病变，建议定期复查，控制血糖。",
  "patient_info": {   
    "name": "张三",
    "sex": "男",
    "age": 21
  },
  "stream": false
}
```

## 系统输出：
系统支持两种输出模式：标准模式和流式模式

### 标准模式（非流式）：
```json
{
  "medications": [
    {
      "medication_name": "人工泪液",
      "dosage": "每次1-2滴",
      "frequency": "每天4次",
      "side_effects": "轻微刺痛感"
    }
  ],
  "treatment_plan": {
    "treatment_type": "药物治疗",
    "treatment_detail": "每天使用人工泪液，避免长时间用眼，定期复查"
  }
}
```

### 流式模式：
流式输出采用 SSE (Server-Sent Events) 技术，每个数据块是一个JSON对象。

单个数据块格式：
```json
{
  "content": "{\"medications\": [{\"medication_name\": \"人工",
  "is_complete": false
}
```

最后一个数据块：
```json
{
  "content": "泪液\"}], \"treatment_plan\": {\"treatment_type\": \"药物治疗\"}}",
  "is_complete": true
}
```

## 提示词工程（Prompt Engineering）

### 系统提示词（System Prompt）
系统提示词用于设置模型的行为和角色定位：
# AI Recommendation System Prompts
```plaintext
你是一位经验丰富的眼科医生AI助手。你的任务是根据患者的诊断和信息提供用药和治疗建议。
你必须严格按照以下JSON格式回复，不要添加任何其他文字或解释：

{
    "medications": [
        {
            "medication_name": "药品名称",
            "dosage": "具体剂量说明",
            "frequency": "用药频率",
            "side_effects": "可能的副作用"
        }
    ],
    "treatment_plan": {
        "treatment_type": "治疗类型（如：药物治疗、手术治疗等）",
        "treatment_detail": "详细的治疗说明"
    }
}

注意事项：
1. 必须严格按照上述JSON格式回复
2. 所有字段都必须填写，不能省略
3. medications字段是一个数组，也就是说你可以推荐多个药品
4. 不要添加任何其他说明文字
5. 确保输出是有效的JSON格式
6. 使用中文回复所有内容"""

RECOMMENDATION_USER_TEMPLATE = """请为以下患者提供用药和治疗建议：

患者信息：
- 姓名：{name}
- 性别：{sex}
- 年龄：{age}岁

诊断信息：
- 疾病：{disease_name}
- 类别：{disease_category}
- 诊断结果：{result}

请严格按照指定的JSON格式提供建议，不要添加任何其他说明文字。
```