# 学习阶段 02：HTTP错误处理与重试机制

## 📌 阶段信息
- **阶段编号**: 02
- **前置要求**: 完成STAGE_01（HTTP基础）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps / 后端开发

---

## 🎯 学习目标

1. 理解为什么需要重试机制
2. 掌握指数退避算法
3. 区分哪些错误应该重试、哪些不应该
4. 理解超时保护的重要性

---

## 📚 核心概念

### 概念1：为什么需要重试？

网络请求可能因以下原因失败：
- 网络抖动（临时断开）
- 服务端过载（503）
- 请求超时

**关键原则**：临时性故障应该重试，永久性故障不应重试。

```
应该重试的情况：
- 5xx 服务端错误（500/502/503/504）
- 网络超时
- 连接失败

不应重试的情况：
- 4xx 客户端错误（400/401/403/404）
  → 请求本身有问题，重试也不会成功
- 已知的业务错误
```

---

### 概念2：指数退避（Exponential Backoff）

**问题**：如果所有客户端同时重试，会造成"惊群效应"，服务端更难恢复。

**解决**：每次重试等待时间翻倍。

```
第1次失败 → 等 1 秒后重试
第2次失败 → 等 2 秒后重试
第3次失败 → 等 4 秒后重试
第4次失败 → 等 8 秒后重试
...
```

**公式**：`wait_time = base * (2 ** attempt)`

**优点**：
- 不会让服务端雪上加霜
- 自适应：如果服务快速恢复，下次重试间隔会自动缩小

---

### 概念3：超时保护（Timeout）

**问题**：请求可能一直卡住，不返回也不报错。

**解决**：设置超时时间，强制放弃。

```python
# 错误示例：无超时设置
resp = requests.get(url)  # 可能永远卡住！

# 正确示例：设置超时
resp = requests.get(url, timeout=10)  # 10秒后强制放弃
```

**timeout参数**：
- `timeout=10`: 连接+读取总共最多10秒
- `timeout=(3, 10)`: 连接最多3秒，读取最多10秒

**SRE原则**：所有网络请求都必须有超时设置！

---

## 💻 项目代码参考

### 来源：modules/scraper.py - 熔断机制

```python
class GooglePlacesClient:
    def __init__(self, api_key: str):
        self.quota_exhausted = False  # 熔断开关
    
    def search(self, query: str):
        # 检查熔断状态
        if self.quota_exhausted:
            return []  # 快速失败，不再请求
        
        try:
            resp = self.session.post(url, timeout=30)
        except requests.RequestException as e:
            print(f"[WARN] 网络异常: {e}")
            return []
        
        # 检测API限流
        if resp.status_code in (403, 429):
            self.quota_exhausted = True  # 触发熔断
            return []
```

**理解要点**：
- `quota_exhausted` 是熔断开关，一旦触发，后续请求直接失败
- 避免持续请求已限流的API，保护账号
- 这是Circuit Breaker模式的基础

---

### 来源：modules/deployer.py - 指数退避重试

```python
MAX_RETRIES = 4  # 最多重试4次

def _request(self, method: str, path: str, **kw) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = self.session.request(method, url, timeout=60, **kw)
            # 成功
            return resp.json()["result"]
        except requests.RequestException:
            wait = min(2 ** attempt, 15)  # 指数退避，最多15秒
            print(f"[RETRY] 等待 {wait}s (第 {attempt}/{MAX_RETRIES} 次)")
            time.sleep(wait)
            continue
    raise RuntimeError(f"重试 {MAX_RETRIES} 次后仍失败")
```

**理解要点**：
- `min(2 ** attempt, 15)` 限制最大等待时间，避免无限增长
- 重试次数有上限，不会无限重试

---

### 来源：pipeline.py - 健康检查重试

```python
PROBE_TIMEOUT = 20
PROBE_RETRIES = 3
PROBE_BACKOFF = 4

def probe_site(url: str, deep: bool = True) -> dict:
    for attempt in range(PROBE_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KL-Agent-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as r:
                result["status"] = r.status
                break  # 成功，跳出循环
        except urllib.error.HTTPError as e:
            result["status"] = e.code
            if e.code >= 500:  # 5xx 才重试
                result["retries"] += 1
                time.sleep(PROBE_BACKOFF * (2 ** attempt))
                continue
            break  # 4xx 不重试
        except Exception as e:
            result["retries"] += 1
            time.sleep(PROBE_BACKOFF * (2 ** attempt))
    
    result["ok"] = result["status"] == 200
    return result
```

**理解要点**：
- 5xx错误重试，4xx不重试
- 使用 `urllib` 标准库（无第三方依赖）

---

## 🔧 动手练习

### 练习2.1：实现指数退避重试

```python
import requests
import time

def fetch_with_retry(url: str, max_retries: int = 3, timeout: int = 10):
    """
    实现带指数退避的HTTP请求
    返回: (success: bool, status_code: int, error: str)
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout)
            return (True, resp.status_code, "")
        
        except requests.Timeout:
            # TODO: 实现指数退避
            wait = ???  # 你来实现
            print(f"超时，{wait}秒后重试 ({attempt+1}/{max_retries})")
            time.sleep(wait)
        
        except requests.RequestException as e:
            return (False, 0, str(e))
    
    return (False, 0, "重试次数用尽")

# 测试
if __name__ == "__main__":
    # 这个URL会延迟5秒响应，测试超时
    fetch_with_retry("https://httpbin.org/delay/5", timeout=2, max_retries=3)
```

### 练习2.2：区分5xx和4xx的重试逻辑

```python
import requests
import time

def fetch_smart(url: str, max_retries: int = 3, timeout: int = 10):
    """
    智能重试：5xx重试，4xx不重试
    返回: (success: bool, status_code: int, error: str)
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout)
            
            if 200 <= resp.status_code < 300:
                return (True, resp.status_code, "")
            
            # TODO: 判断是否应该重试
            # 5xx重试，4xx不重试
            
        except requests.Timeout:
            # TODO: 指数退避重试
            pass
        
        except requests.RequestException as e:
            return (False, 0, str(e))
    
    return (False, 0, "重试次数用尽")

# 测试
test_urls = [
    ("https://httpbin.org/status/200", "成功"),
    ("https://httpbin.org/status/404", "404不应该重试"),
    ("https://httpbin.org/status/500", "500应该重试"),
    ("https://httpbin.org/status/502", "502应该重试"),
]

for url, desc in test_urls:
    print(f"\n测试: {desc}")
    success, status, error = fetch_smart(url)
    print(f"结果: {status}")
```

### 练习2.3：实现熔断器

```python
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class CircuitBreaker:
    """
    简化的熔断器
    - 连续失败N次后熔断
    - 熔断后直接返回失败，不再请求
    """
    failure_threshold: int = 3  # 连续失败N次后熔断
    failure_count: int = 0
    is_open: bool = False  # 熔断状态
    
    def call(self, url: str) -> Optional[dict]:
        """
        调用API，如果熔断器开启则直接返回None
        """
        # TODO: 实现熔断逻辑
        pass

# 测试
breaker = CircuitBreaker(failure_threshold=2)

# 连续请求失败的服务
for i in range(5):
    result = breaker.call("https://httpbin.org/status/500")
    print(f"请求{i+1}: {'成功' if result else '失败/熔断'}")
    print(f"熔断器状态: {'开启' if breaker.is_open else '关闭'}")
```

---

## ✅ 验收标准

1. **问**：为什么4xx错误不应该重试？
   **答**：4xx是客户端错误，请求本身有问题。比如404是资源不存在，重试多少次都不存在。

2. **问**：为什么使用指数退避而不是固定等待时间？
   **答**：
   - 避免所有客户端同时重试（惊群效应）
   - 给服务端恢复时间
   - 自适应：如果服务快速恢复，不会等太久

3. **问**：timeout=10 是什么意思？
   **答**：请求最多等待10秒，超过就放弃。这是防止请求卡死的关键保护措施。

4. **问**：什么是熔断（Circuit Breaker）？
   **答**：当外部服务持续不可用时，不再继续请求，直接返回失败。避免资源浪费，快速失败。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_03**: API调用与OpenAI SDK

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段02：HTTP错误处理与重试机制。

我已完成：
- 理解为什么需要重试（处理临时故障）
- 掌握指数退避算法（wait = base * 2^attempt）
- 理解5xx重试、4xx不重试的区别
- 理解超时保护的重要性
- 了解熔断器（Circuit Breaker）概念

请帮我：
1. 检查我对以下代码的理解是否正确
2. 给我一个综合练习来巩固这些概念

我写的重试代码：
[粘贴你的练习代码]

参考项目代码：
- modules/scraper.py 实现了 quota_exhausted 熔断开关
- modules/deployer.py 实现了 MAX_RETRIES 指数退避
- pipeline.py 实现了 5xx重试/4xx不重试 的逻辑
```