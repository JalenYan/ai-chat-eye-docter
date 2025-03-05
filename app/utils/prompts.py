"""
Prompt engineering utilities for the eye doctor AI chat application.
This module contains system prompts, user input templates, and specialized prompts
for different types of questions related to eye diseases.
"""

# System prompt that sets the AI's behavior and role
SYSTEM_PROMPT = """
你是一位专业的眼科医学顾问，基于患者的眼底检查结果和相关问题提供专业咨询。
你的职责是：
1. 解释眼科检查结果和诊断的含义
2. 回答患者关于眼部疾病、治疗方案和用药的问题
3. 提供基于循证医学的专业建议
4. 使用通俗易懂的语言解释专业概念
5. 在必要时强调寻求正规医疗机构和医生进一步诊疗的重要性

注意事项：
- 保持友善、耐心和专业的态度
- 避免做出确定性的诊断，应强调这只是辅助分析
- 避免开具处方或替代医生的治疗决策
- 当无法确定答案时，坦诚承认并建议咨询专业医生
- 回答应基于提供的病历信息和眼科专业知识
- 提供信息时应尽量引用可靠的医学资源
"""

# User input processing template
USER_INPUT_TEMPLATE = """
根据您的眼底检查结果：
- 诊断: {disease_name} ({disease_category})
- 检查结果: {result}
- 备注: {remark}
- 治疗计划: {treatment_plan}
- 用药信息: {medications}

您的问题是: {question}
"""

# Specialized prompts for different question types

# 1. Disease explanation questions
DISEASE_EXPLANATION_PROMPT = """
请针对{disease_name}提供以下信息：
1. 简明的疾病定义
2. 常见病因和风险因素
3. 该疾病的典型症状和体征
4. 可能的发展过程和预后
5. 该疾病与患者当前症状的关联

回答应该通俗易懂，避免过多专业术语，必要时对专业概念进行解释。同时，基于患者的具体情况（{result}）给出针对性说明。
"""

# 2. Treatment plan questions
TREATMENT_PLAN_PROMPT = """
请基于患者的{disease_name}诊断结果（{result}）和当前建议的治疗方案（{treatment_plan}），提供：
1. 该疾病常规治疗方法概述
2. 当前推荐治疗方案的原理和目的
3. 治疗的预期效果和时间周期
4. 治疗过程中的注意事项
5. 何时应该随访或复查

强调治疗方案的重要性，但避免替代医生的临床决策，建议患者遵循专业医生的具体指导。
"""

# 3. Medication consultation questions
MEDICATION_PROMPT = """
针对患者使用的药物（{medications}），请提供：
1. 药物的主要作用机制
2. 正确的使用方法和频率
3. 常见副作用及其处理方法
4. 特殊注意事项（如禁忌症、药物相互作用）
5. 用药依从性的重要性

同时，根据患者的具体情况（{disease_name}和{result}），解释为何医生选择这种药物治疗。
"""

# 4. Prevention and lifestyle questions
PREVENTION_LIFESTYLE_PROMPT = """
针对{disease_name}，请提供以下生活方式和预防建议：
1. 日常护眼和自我监测方法
2. 饮食建议和营养补充
3. 适宜和不适宜的活动
4. 环境因素控制（如光线、屏幕使用等）
5. 定期随访和检查的时间表

这些建议应结合患者的具体情况（{result}和{remark}），着重强调对疾病管理特别重要的生活方式调整。
"""

# 5. Severity and prognosis questions
SEVERITY_PROGNOSIS_PROMPT = """
关于{disease_name}的严重性和预后，请基于患者的检查结果（{result}）提供：
1. 当前病情严重程度的客观评估
2. 该疾病的自然病程和可能的进展
3. 及时治疗与否对预后的影响
4. 可能出现的并发症及其预防
5. 长期管理和监测的重要性

保持平衡的态度，既不过度淡化病情，也不引起不必要的恐慌。强调个体差异和积极治疗的价值。
"""

# Standard answer format
ANSWER_FORMAT = """
<回答内容，包括：
- 对问题的直接回答
- 相关医学解释
- 实用建议
- 必要的警示或提醒>

<参考资料（如适用）：
- 参考文献或指南名称
- 发布机构
- 年份>
"""

# Knowledge domain restrictions
KNOWLEDGE_DOMAIN_RESTRICTIONS = """
模型应限制在以下眼科专业领域内提供答案：
1. 常见眼科疾病的基础知识
2. 眼底疾病的诊断和治疗常识
3. 眼科用药和治疗方案的一般性知识
4. 眼部保健和预防措施
5. 眼科检查和随访的一般性建议

对于超出上述范围的问题，模型应礼貌地表示无法提供专业答案，并建议咨询专业医生。
"""

# Helper function to format medication information
def format_medications(medications):
    """Format medication information into a readable string"""
    if not medications:
        return "无"
    
    formatted = []
    for med in medications:
        med_info = f"{med.get('medication_name', '未知药物')}"
        
        dosage = med.get('dosage')
        if dosage:
            med_info += f"，剂量：{dosage}"
            
        frequency = med.get('frequency')
        if frequency:
            med_info += f"，频率：{frequency}"
            
        side_effects = med.get('side_effects')
        if side_effects:
            med_info += f"，可能的副作用：{side_effects}"
            
        formatted.append(med_info)
    
    return "；".join(formatted)

# Helper function to construct the user input from request data
def construct_user_input(request_data):
    """
    Construct a formatted user input from the request data
    
    Args:
        request_data: Dictionary containing patient information and question
        
    Returns:
        Formatted string with patient information and question
    """
    disease_name = request_data.get('disease_name', '未知疾病')
    disease_category = request_data.get('disease_category', '未知类别')
    result = request_data.get('result', '无检查结果')
    remark = request_data.get('remark', '无备注')
    
    # Get treatment plan
    treatment_plan = "无治疗计划"
    if 'treatment_plan' in request_data and 'treatment_detail' in request_data['treatment_plan']:
        treatment_plan = request_data['treatment_plan']['treatment_detail']
    
    # Format medications
    medications = format_medications(request_data.get('medications', []))
    
    # Get the question
    question = request_data.get('question', '无具体问题')
    
    # Format using the template
    return USER_INPUT_TEMPLATE.format(
        disease_name=disease_name,
        disease_category=disease_category,
        result=result,
        remark=remark,
        treatment_plan=treatment_plan,
        medications=medications,
        question=question
    )

# Helper function to get the most appropriate specialized prompt based on the question
def get_specialized_prompt(request_data):
    """
    Determine which specialized prompt to use based on the question
    
    Args:
        request_data: Dictionary containing patient information and question
        
    Returns:
        Specialized prompt string formatted with patient data
    """
    question = request_data.get('question', '').lower()
    disease_name = request_data.get('disease_name', '未知疾病')
    result = request_data.get('result', '无检查结果')
    remark = request_data.get('remark', '无备注')
    
    # Get treatment plan
    treatment_plan = "无治疗计划"
    if 'treatment_plan' in request_data and 'treatment_detail' in request_data['treatment_plan']:
        treatment_plan = request_data['treatment_plan']['treatment_detail']
    
    # Format medications
    medications = format_medications(request_data.get('medications', []))
    
    # Check question type
    if any(keyword in question for keyword in ['什么病', '这个病是什么', '为什么会得', '病因']):
        return DISEASE_EXPLANATION_PROMPT.format(
            disease_name=disease_name,
            result=result
        )
    
    elif any(keyword in question for keyword in ['怎么治', '如何治疗', '治疗方法', '需要手术']):
        return TREATMENT_PLAN_PROMPT.format(
            disease_name=disease_name,
            result=result,
            treatment_plan=treatment_plan
        )
    
    elif any(keyword in question for keyword in ['药', '用药', '药物', '副作用']):
        return MEDICATION_PROMPT.format(
            medications=medications,
            disease_name=disease_name,
            result=result
        )
    
    elif any(keyword in question for keyword in ['预防', '生活', '日常', '饮食', '护眼']):
        return PREVENTION_LIFESTYLE_PROMPT.format(
            disease_name=disease_name,
            result=result,
            remark=remark
        )
    
    elif any(keyword in question for keyword in ['严重吗', '会好吗', '预后', '影响视力']):
        return SEVERITY_PROGNOSIS_PROMPT.format(
            disease_name=disease_name,
            result=result
        )
    
    # Default case - no specialized prompt
    return ""

# Main function to construct the complete prompt
def construct_prompt(request_data):
    """
    Construct the complete prompt for the LLM
    
    Args:
        request_data: Dictionary containing patient information and question
        
    Returns:
        Tuple of (system_prompt, user_message) to send to the LLM
    """
    # Basic user input
    user_input = construct_user_input(request_data)
    
    # Get specialized prompt if applicable
    specialized_prompt = get_specialized_prompt(request_data)
    
    # Combine user input with specialized prompt if exists
    if specialized_prompt:
        user_message = f"{user_input}\n\n{specialized_prompt}"
    else:
        user_message = user_input
    
    return SYSTEM_PROMPT, user_message 