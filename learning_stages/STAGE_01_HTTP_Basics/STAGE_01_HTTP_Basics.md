# 学习阶段 01：HTTP基础与请求生命周期

## 📌 阶段信息
- **阶段编号**: 01
- **前置要求**: 无（从零开始）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps / 后端开发

---

## 🎯 学习目标

1. 理解HTTP协议的基本工作原理
2. 掌握HTTP状态码分类和含义
3. 理解请求头和响应头的作用
4. 能够使用Python发送HTTP请求

---

## 📚 核心概念

### 概念1：HTTP是什么？

HTTP（HyperText Transfer Protocol）是无状态的请求-响应协议。

```
客户端                          服务端
   │                              │
   │──── GET /index.html ────────▶│  请求
   │                              │
   │◀─── 200 OK + HTML内容 ───────│  响应
   │                              │
```

**关键特点**：
- 无状态：每次请求独立，服务端不记住之前请求
- 请求-响应模式：客户端发起，服务端响应
- 基于TCP：需要先建立TCP连接

---

### 概念2：HTTP状态码

```
1xx - 信息性响应（很少见）
  100 Continue: 继续发送请求体

2xx - 成功
  200 OK: 请求成功
  201 Created: 资源创建成功
  204 No Content: 成功但无返回内容

3xx - 重定向
  301 Moved Permanently: 永久重定向
  302 Found: 临时重定向
  304 Not Modified: 缓存未修改

4xx - 客户端错误（你的错）
  400 Bad Request: 请求格式错误
  401 Unauthorized: 未认证
  403 Forbidden: 已认证但无权限
  404 Not Found: 资源不存在
  429 Too Many Requests: 请求太频繁

5xx - 服务端错误（服务端的问题）
  500 Internal Server Error: 代码异常
  502 Bad Gateway: 上游服务不可达
  503 Service Unavailable: 服务过载
  504 Gateway Timeout: 上游超时
```

**面试常问**：
- 429怎么处理？→ 重试，但要指数退避
- 500和502有什么区别？→ 500是应用代码错误，502是上游服务不可达
- 401和403有什么区别？→ 401是未登录，403是登录了但没权限

---

### 概念3：请求头（Headers）

常见的请求头：

```
User-Agent: Mozilla/5.0 ...    # 客户端身份
Content-Type: application/json # 请求体格式
Authorization: Bearer xxx       # 认证信息
Accept: application/json        # 期望的响应格式
```

**为什么要设置User-Agent？**
- 很多API/网站会拒绝默认的Python requests User-Agent
- 在本项目builder.py中，我们设置了自定义User-Agent绕过WAF

---

## 💻 项目代码参考

### 来源：modules/scraper.py

```python
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/37.36")

class GooglePlacesClient:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        # 设置请求头
        self.session.headers.update({
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        })
```

**理解要点**：
- `requests.Session()` 复用TCP连接，减少握手开销
- `headers.update()` 设置公共请求头
- `User-Agent` 伪装成浏览器，避免被拦截

---

### 来源：modules/builder.py

```python
SAFE_HEADERS = {"User-Agent": "kl-restaurant-agent/2.0"}

class ZhipuClient:
    def _client(self):
        return OpenAI(
            api_key=self._args[0],
            base_url=self._args[1],
            default_headers=SAFE_HEADERS,  # 绕过网关 WAF
            timeout=180,
        )
```

**理解要点**：
- 智谱API的网关有WAF，会拦截默认的OpenAI SDK User-Agent
- 必须自定义User-Agent才能正常调用

---

## 🔧 动手练习

### 练习1.1：发送GET请求

```python
import requests

# 发送一个简单的GET请求
resp = requests.get("https://httpbin.org/get")
print(f"状态码: {resp.status_code}")
print(f"响应内容: {resp.json()}")
```

### 练习1.2：处理不同状态码

```python
import requests

test_urls = [
    "https://httpbin.org/status/200",  # 成功
    "https://httpbin.org/status/404",  # 资源不存在
    "https://httpbin.org/status/500",  # 服务端错误
    "https://httpbin.org/status/429",  # 限流
]

for url in test_urls:
    resp = requests.get(url)
    print(f"URL: {url}")
    print(f"状态码: {resp.status_code}")
    
    # 判断是否成功
    if 200 <= resp.status_code < 300:
        print("结果: 成功")
    elif 400 <= resp.status_code < 500:
        print("结果: 客户端错误，不应重试")
    elif resp.status_code >= 500:
        print("结果: 服务端错误，可以考虑重试")
    print()
```

### 练习1.3：设置请求头

```python
import requests

headers = {
    "User-Agent": "MyLearningApp/1.0",
    "Accept": "application/json",
}

resp = requests.get("https://httpbin.org/headers", headers=headers)
print(resp.json()["headers"])  # 查看服务端收到的请求头
```

---

## ✅ 验收标准

完成以下问题，说明你掌握了本阶段内容：

1. **问**：HTTP是无状态协议，这意味着什么？
   **答**：每次请求独立，服务端不记住之前的请求。需要认证的场景要用Token/Session。

2. **问**：收到429状态码应该怎么处理？
   **答**：请求太频繁，应该等待一段时间后重试。生产环境用指数退避（1s, 2s, 4s...）。

3. **问**：为什么有时候需要自定义User-Agent？
   **答**：很多API/网站会拒绝默认的requests User-Agent。在本项目中，智谱API的WAF会拦截默认User-Agent，必须自定义才能调用。

4. **问**：500和502有什么区别？
   **答**：500是应用代码异常（比如Python报错），502是上游服务不可达（比如Nginx反向代理的后端服务挂了）。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_02**: HTTP错误处理与重试机制

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段01：HTTP基础。

我已完成：
- HTTP协议基本原理（无状态、请求-响应模式）
- 状态码分类（2xx成功、4xx客户端错误、5xx服务端错误）
- 请求头的作用（User-Agent、Content-Type等）

请帮我：
1. 确认我对上述概念的理解是否正确
2. 如果理解正确，给我一个综合练习，巩固这些知识
3. 如果有不清楚的地方，请解释

参考项目代码：
- modules/scraper.py 使用 requests.Session() 和自定义 User-Agent
- modules/builder.py 需要自定义 User-Agent 绕过 WAF
```