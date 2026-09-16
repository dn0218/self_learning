# 学习阶段 03：API调用与OpenAI SDK

## 📌 阶段信息
- **阶段编号**: 03
- **前置要求**: 完成STAGE_02（HTTP重试机制）
- **预计时间**: 2-3天
- **目标岗位**: SRE / AI Infra / AI Prompt Engineer

---

## 🎯 学习目标

1. 理解OpenAI SDK的工作原理
2. 掌握不同LLM API的兼容调用方式
3. 理解temperature、max_tokens等参数的作用
4. 能够设计基础的Prompt

---

## 📚 核心概念

### 概念1：OpenAI SDK架构

```
你的代码
    │
    ▼
OpenAI SDK (Python客户端库)
    │
    ▼
HTTP请求 (POST /v1/chat/completions)
    │
    ▼
LLM服务端 (OpenAI API / 智谱API / 其他兼容服务)
    │
    ▼
HTTP响应 (JSON格式的生成结果)
```

**关键理解**：
- OpenAI SDK本质上是HTTP客户端的封装
- 任何兼容OpenAI API格式的服务都可以用同一个SDK调用
- 只需要改`base_url`和`api_key`

---

### 概念2：重要参数解释

```python
response = client.chat.completions.create(
    model="gpt-4",           # 使用哪个模型
    messages=[...],          # 对话历史
    temperature=0.7,         # 随机性（0-2）
    max_tokens=1000,         # 最大输出长度
    top_p=0.9,               # 核采样（可选）
    frequency_penalty=0,     # 频率惩罚（可选）
    presence_penalty=0,      # 存在惩罚（可选）
)
```

**temperature详解**：
```
temperature=0   → 最确定性，每次输出几乎相同（代码生成推荐）
temperature=0.7 → 适中有创造性（一般对话推荐）
temperature=1.0+ → 非常随机（创意写作可能用到）
```

**max_tokens详解**：
```
max_tokens=100  → 最多输出约100个英文单词
max_tokens=4000 → 足够生成一篇长文

注意：推理模型（如GLM-4/5）的"思考过程"也计入tokens
所以推理模型需要设置更大的max_tokens
```

---

### 概念3：消息格式（Messages）

```python
messages = [
    {"role": "system", "content": "你是一个专业的翻译"},    # 定义角色
    {"role": "user", "content": "翻译这句话：Hello"},      # 用户输入
    {"role": "assistant", "content": "你好"},              # AI之前的回复（多轮对话）
    {"role": "user", "content": "翻译：Thank you"},       # 用户继续
]
```

**三种角色**：
- `system`: 系统指令，定义AI的角色和行为规范
- `user`: 用户输入
- `assistant`: AI的回复（多轮对话时需要）

---

## 💻 项目代码参考

### 来源：modules/builder.py

```python
from openai import OpenAI

class ZhipuClient:
    """智谱GLM，OpenAI SDK兼容"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        self._inner = None
        self._args = (api_key, base_url)
    
    def _client(self):
        if self._inner is None:
            self._inner = OpenAI(
                api_key=self._args[0],
                base_url=self._args[1],           # 关键：替换为智谱API
                default_headers=SAFE_HEADERS,     # 关键：自定义请求头绕过WAF
                timeout=180,
            )
        return self._inner
    
    def chat_json(self, system: str, user: str) -> dict:
        """发起对话并解析JSON"""
        resp = self._client().chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=GEN_TEMPERATURE,  # 0.7
            max_tokens=MAX_TOKENS,         # 6000
        )
        content = resp.choices[0].message.content
        return parse_json_loose(content)
```

**理解要点**：
- `base_url` 改为智谱API地址，SDK就能调用智谱模型
- `default_headers` 绕过智谱API的WAF限制
- `timeout=180` 给足够时间（生成网页可能较慢）

---

### 来源：modules/builder.py - Prompt设计

```python
SYSTEM_PROMPT = """You are an elite hospitality web architect: 
part UI/UX designer, part conversion copywriter, serving premium & boutique 
restaurants in Kuala Lumpur (RM40+ per person).

1. Color Psychology:
   - Fine dining: Deep burgundy, gold accents (sophistication)
   - Cafe: Warm browns, earthy greens (cozy)

2. Typography:
   - Headlines: Playfair Display (elegant serif)
   - Body: Inter (clean sans-serif)

3. Output: Valid HTML with Tailwind CSS classes.
"""
```

**Prompt设计原则**：
1. **角色定义**："You are..." 定义AI的专业领域
2. **任务说明**：详细描述要做什么
3. **约束条件**：输出格式、风格要求
4. **示例**：给几个好例子，AI会模仿

---

### 来源：modules/builder.py - JSON解析

```python
def parse_json_loose(text: str) -> dict:
    """
    容错解析：AI可能返回带markdown围栏的JSON
    输入: ```json\n{"name": "test"}\n```
    输出: {"name": "test"}
    """
    # 去除markdown代码块
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S)
    # 提取第一个JSON对象
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("输出中未找到 JSON 对象")
    return json.loads(m.group(0))
```

**为什么需要这个函数？**
- AI输出不可预测，可能前后有额外文字
- 可能用 ```json ... ``` 包裹
- 需要容错解析提取真正的JSON

---

## 🔧 动手练习

### 练习3.1：调用OpenAI兼容API

```python
from openai import OpenAI

# TODO: 替换为你的API Key
client = OpenAI(
    api_key="your_api_key",
    base_url="https://open.bigmodel.cn/api/paas/v4/",  # 智谱API
)

# 发送一个简单的请求
response = client.chat.completions.create(
    model="glm-4-flash",  # 智谱的便宜模型
    messages=[
        {"role": "user", "content": "你好，请用一句话介绍Python"},
    ],
)

print(response.choices[0].message.content)
```

### 练习3.2：控制输出随机性

```python
from openai import OpenAI

client = OpenAI(...)

# 测试不同temperature
prompts = ["给我讲一个笑话"]

for temp in [0, 0.5, 1.0]:
    print(f"\n=== temperature={temp} ===")
    for i in range(3):
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompts[0]}],
            temperature=temp,
        )
        print(f"第{i+1}次: {response.choices[0].message.content[:50]}...")
```

**观察**：
- temp=0 时，三次输出应该几乎相同
- temp=1 时，三次输出应该差异较大

### 练习3.3：生成结构化JSON

```python
from openai import OpenAI
import json
import re

client = OpenAI(...)

# 设计Prompt让它输出JSON
system_prompt = """你是一个餐厅菜单生成器。
输出必须是有效的JSON格式，不要有任何额外文字。
格式：
{
    "name": "餐厅名称",
    "dishes": [
        {"name": "菜名", "price": "RM 28.00"}
    ]
}"""

user_prompt = "为一家马来西亚餐厅生成3道招牌菜"

response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0.3,  # 较低温度，更稳定
)

# 解析JSON
def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S)
    m = re.search(r"\{.*\}", text, flags=re.S)
    return json.loads(m.group(0))

result = parse_json(response.choices[0].message.content)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## ✅ 验收标准

1. **问**：temperature参数的作用是什么？
   **答**：控制输出的随机性。0最确定（适合代码），1最有创意（适合写作）。本项目用0.7平衡。

2. **问**：为什么推理模型需要更大的max_tokens？
   **答**：推理模型的"思考过程"也计入tokens。如果max_tokens太小，输出会被截断。

3. **问**：为什么需要parse_json_loose函数？
   **答**：AI输出不可预测，可能带markdown围栏或额外文字。需要容错解析。

4. **问**：如何用OpenAI SDK调用其他LLM（如智谱）？
   **答**：只需修改`base_url`参数指向兼容的API地址，其他代码不变。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_04**: Prompt工程基础

---

## 📝 AI Prompt（用于新对话）

```
我正在学习AI工程相关技术，当前处于阶段03：API调用与OpenAI SDK。

我已完成：
- 理解OpenAI SDK是HTTP客户端的封装
- 掌握通过base_url调用不同LLM服务
- 理解temperature（随机性）和max_tokens（输出长度）参数
- 掌握messages格式（system/user/assistant）
- 能够生成和解析JSON输出

请帮我：
1. 检查我对以下代码的理解是否正确
2. 给我一个综合练习来巩固这些概念

我写的API调用代码：
[粘贴你的练习代码]

参考项目代码：
- modules/builder.py 的 ZhipuClient 类
- 使用 base_url 指向智谱API
- 使用 default_headers 绕过WAF
- temperature=0.7, max_tokens=6000
```