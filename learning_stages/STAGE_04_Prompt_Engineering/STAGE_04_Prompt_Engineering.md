# 学习阶段 04：Prompt工程基础

## 📌 阶段信息
- **阶段编号**: 04
- **前置要求**: 完成STAGE_03（API调用）
- **预计时间**: 2-3天
- **目标岗位**: AI Prompt Engineer / AI Infra

---

## 🎯 学习目标

1. 理解Prompt的基本结构和设计原则
2. 掌握角色定义、任务拆解、输出格式控制
3. 理解Few-shot示例的作用
4. 能够优化Prompt提高输出质量

---

## 📚 核心概念

### 概念1：Prompt的基本结构

一个好的Prompt通常包含以下部分：

```
1. 角色定义（Role）
   "你是一个专业的..."

2. 任务说明（Task）
   "请帮我..."

3. 背景信息（Context）
   "这是一个关于..."

4. 约束条件（Constraints）
   "输出必须是..."
   "长度不超过..."

5. 示例（Examples）
   "例如：输入A，输出B"
```

---

### 概念2：角色定义的重要性

**差的Prompt**：
```
翻译这个句子：Hello
```

**好的Prompt**：
```
你是一位专业的英中翻译，精通商务英语和日常对话风格。
请将以下英文翻译成自然流畅的中文，保持原文的语气和情感：
Hello
```

**为什么角色定义重要？**
- 让AI知道应该用什么样的"知识库"回答
- 定义输出的风格和水平
- 避免AI用不恰当的方式回答

---

### 概念3：输出格式控制

**JSON输出**：
```
输出必须是有效的JSON格式，包含以下字段：
{
    "name": "名称",
    "description": "描述",
    "price": "价格"
}
不要有任何额外文字或解释。
```

**Markdown输出**：
```
输出使用Markdown格式：
- 一级标题用 #
- 列表用 -
- 代码块用 ```
```

**结构化文本**：
```
按以下格式输出：
【菜名】价格
【简介】一句话描述
【推荐理由】为什么值得尝试
```

---

### 概念4：Few-shot示例

**无示例（Zero-shot）**：
```
将以下菜品分类：
炒饭
→ [AI可能不知道怎么分类]
```

**有示例（Few-shot）**：
```
将菜品分类为主食、配菜或饮品。
示例：
输入：炒饭 → 输出：主食
输入：可乐 → 输出：饮品
输入：炒时蔬 → 输出：配菜

输入：面条
→ [AI会按照示例的模式回答：主食]
```

**Few-shot的好处**：
- 让AI理解你想要的格式
- 减少歧义和错误
- 提高输出一致性

---

## 💻 项目代码参考

### 来源：modules/builder.py - 完整Prompt示例

```python
SYSTEM_PROMPT = """You are an elite hospitality web architect: part UI/UX designer, 
part conversion copywriter, serving premium & boutique restaurants in Kuala Lumpur 
(RM40+ per person). You understand visual branding (colour psychology, typography 
pairing, imagery placement) and write refined, appetizing, credible copy — never 
cheesy, never exaggerated.

【设计规则】
1. Color Psychology:
   - Fine dining: Deep burgundy, gold accents (sophistication)
   - Cafe: Warm browns, earthy greens (cozy)
   - Modern Asian: Jade green, charcoal, warm whites

2. Typography:
   - Headlines: Playfair Display (elegant serif)
   - Body: Inter (clean sans-serif)

3. Conversion Elements:
   - Clear CTA above the fold
   - Social proof (reviews) near decision points
   - Price displayed clearly

【输出要求】
- 输出完整的HTML文档
- 使用Tailwind CSS类
- 包含响应式设计（mobile-first）
- 双语切换按钮（中/英）
"""
```

**分析这个Prompt**：
1. **角色定义**：精英级酒店网页设计师
2. **领域限定**：吉隆坡高端餐厅（RM40+）
3. **技能说明**：视觉品牌、字体搭配、转化文案
4. **设计规则**：颜色心理学、字体选择、转化元素
5. **输出约束**：HTML + Tailwind + 响应式 + 双语

---

### 来源：modules/builder.py - 动态Prompt构建

```python
def build_user_prompt(lead: Lead, reviews: list, hours: list) -> str:
    """根据商家数据动态构建Prompt"""
    
    prompt = f"""
为以下餐厅生成一个高质量网页：

【基本信息】
- 餐厅名称：{lead.name}
- 地址：{lead.address}
- 菜系：{lead.cuisine}
- 评分：{lead.rating}/5 ({lead.reviews}条评价)
- 电话：{lead.phone}

【真实评论】
"""
    for r in reviews[:3]:
        prompt += f"- {r['author']}: \"{r['text'][:100]}...\" ({r['rating']}星)\n"
    
    prompt += f"""
【营业时间】
"""
    for h in hours:
        prompt += f"- {h}\n"
    
    prompt += """
【要求】
1. 使用提供的真实评论，不要编造
2. 突出招牌菜和特色
3. 包含在线预订/外卖链接
4. 整体风格符合餐厅定位
"""
    
    return prompt
```

**理解要点**：
- Prompt可以动态构建，注入真实数据
- 使用真实评论提高内容可信度
- 明确列出要求，AI会逐一遵守

---

## 🔧 动手练习

### 练习4.1：改进一个差的Prompt

**原始Prompt（差）**：
```
帮我写一个餐厅介绍
```

**问题**：
- 没有角色定义
- 没有餐厅信息
- 没有格式要求

**请改进这个Prompt**，要求：
1. 添加角色定义
2. 添加具体餐厅信息（虚构一个）
3. 指定输出格式（JSON或HTML）

---

### 练习4.2：Few-shot示例设计

设计一个Prompt，让AI把菜品描述翻译成简短的营销文案：

```python
# 要求的输入输出格式：
# 输入："新鲜扇贝，蒜蓉粉丝蒸制"
# 输出："鲜嫩扇贝遇上蒜香粉丝，一口海洋的味道"

# 请设计完整的Prompt（包含3个Few-shot示例）
```

---

### 练习4.3：格式控制

设计一个Prompt，生成餐厅菜单的JSON：

```json
期望输出：
{
    "restaurant": "老四川",
    "cuisine": "川菜",
    "dishes": [
        {
            "name": "水煮鱼",
            "price": "RM 48",
            "tags": ["辣", "招牌"],
            "description": "鲜嫩鱼片配麻辣红油..."
        }
    ]
}
```

**要求**：
- 输出必须是纯JSON，无额外文字
- 包含至少5道菜
- 每道菜有name/price/tags/description

---

## ✅ 验收标准

1. **问**：一个好的Prompt应该包含哪些部分？
   **答**：角色定义、任务说明、背景信息、约束条件、示例（可选）

2. **问**：什么是Few-shot？有什么好处？
   **答**：在Prompt中给出输入输出示例。好处：让AI理解格式、减少错误、提高一致性。

3. **问**：如何让AI输出纯JSON？
   **答**：明确要求"输出必须是有效的JSON格式，不要有任何额外文字"，可能还需要后处理去除markdown围栏。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_05**: Linux进程与系统监控

---

## 📝 AI Prompt（用于新对话）

```
我正在学习AI Prompt工程，当前处于阶段04：Prompt工程基础。

我已完成：
- 理解Prompt的基本结构（角色/任务/背景/约束/示例）
- 掌握角色定义的重要性
- 掌握输出格式控制（JSON/Markdown/结构化文本）
- 理解Few-shot示例的作用

请帮我：
1. 评价我设计的Prompt质量
2. 给出改进建议
3. 给我一个进阶练习

我设计的Prompt：
[粘贴你的练习结果]

参考项目代码：
- modules/builder.py 的 SYSTEM_PROMPT 包含完整的设计规则
- build_user_prompt() 函数动态注入商家数据
```