# 学习阶段 09：Web安全基础

## 📌 阶段信息
- **阶段编号**: 09
- **前置要求**: 完成STAGE_08（幂等性）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps / 后端开发

---

## 🎯 学习目标

1. 了解OWASP Top 10常见漏洞
2. 理解路径穿越攻击和防御
3. 理解XSS攻击和防御
4. 理解认证安全（Token存储）

---

## 📚 核心概念

### 概念1：OWASP Top 10

**2021版最关键的10个Web安全风险**：

```
A01: Broken Access Control（权限控制缺失）
     → 水平越权：访问其他用户数据
     → 垂直越权：普通用户访问管理功能

A02: Cryptographic Failures（加密失败）
     → 明文存储密码
     → 使用弱哈希（MD5）

A03: Injection（注入攻击）
     → SQL注入
     → 命令注入

A04: Insecure Design（不安全设计）
     → 业务逻辑漏洞

A05: Security Misconfiguration（安全配置错误）
     → 默认密码
     → 开放不必要的端口

A06: Vulnerable Components（脆弱组件）
     → 使用有漏洞的依赖

A07: Auth Failures（认证失败）
     → 弱密码
     → 无登录限流

A08: Data Integrity Failures（数据完整性失败）
     → 不安全的反序列化

A09: Logging Failures（日志不足）
     → 无法溯源攻击

A10: SSRF（服务端请求伪造）
     → 让服务器访问内网
```

---

### 概念2：路径穿越（Path Traversal）

**攻击原理**：
```
正常请求：
GET /files?name=document.pdf
服务器读取：/var/www/files/document.pdf

攻击请求：
GET /files?name=../../../etc/passwd
服务器读取：/var/www/files/../../../etc/passwd
                     ↓ 解析后
                   /etc/passwd  ← 系统文件泄露！
```

**防御方法**：
```python
from pathlib import Path

def safe_read_file(base_dir: str, filename: str) -> str | None:
    """
    安全的文件读取
    """
    # 1. 检查危险字符
    if not filename or "\x00" in filename or ".." in filename:
        return None
    
    # 2. 规范化路径
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    # 3. 关键检查：目标必须在base目录内
    if not target.is_relative_to(base):
        return None  # 阻止攻击！
    
    return target.read_text()
```

**本项目实现**（portal/app.py）：
```python
def safe_path(slug: str, rel: str) -> Path | None:
    """
    clients/<slug>/<rel> 规范化后必须仍在 clients/<slug>/ 内
    """
    if not rel or "\x00" in rel or not slug or "/" in slug or ".." in slug:
        return None
    base = (CLIENTS_DIR / slug).resolve()
    target = (base / rel).resolve()
    if not target.is_relative_to(base):
        return None
    return target
```

---

### 概念3：XSS（跨站脚本攻击）

**攻击原理**：
```
攻击者提交：
<script>alert(document.cookie)</script>

存储在数据库中

其他用户查看时：
<div>用户输入：<script>alert(document.cookie)</script></div>
                         ↑ 浏览器执行JS！

攻击者获取用户Cookie → 劫持账户
```

**防御方法**：
```python
import html

# 方法1：输出转义
def render_user_input(text: str) -> str:
    return html.escape(text)
    # < → &lt;
    # > → &gt;
    # " → &quot;

# 方法2：输入过滤（移除危险标签）
def sanitize_input(text: str) -> str:
    import re
    # 移除script标签
    text = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.I|re.S)
    # 移除事件属性
    text = re.sub(r"\bon[a-z]+\s*=", "", text, flags=re.I)
    return text
```

**本项目实现**（portal/app.py）：
```python
def _strip_scripts(s: str) -> str:
    """剥离script/iframe/object块"""
    _SCRIPT_RE = re.compile(
        r"<\s*(script|iframe|object|embed)[^>]*>.*?<\s*/\s*\1\s*>",
        re.I | re.S)
    return _SCRIPT_RE.sub("", s)

def _clean_str(v, limit: int) -> str:
    """清理用户输入"""
    return _strip_scripts(v.strip())[:limit]
```

---

### 概念4：Token安全存储

**错误做法**：
```python
# 明文存储Token
tokens = {
    "token_abc123": {"slug": "chez_gaston"}
}
# 如果数据库泄露，所有Token都暴露！
```

**正确做法**（本项目）：
```python
import hashlib
import secrets

def gen_token(slug: str) -> str:
    # 生成随机Token
    token = f"klp_{secrets.token_urlsafe(32)}"
    
    # 库中只存哈希，不存明文
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    tokens[token_hash] = {"slug": slug}
    
    # 明文只显示一次
    return token

def auth_slug(token: str) -> str | None:
    # 验证时也用哈希
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return tokens.get(token_hash, {}).get("slug")
```

**为什么用SHA256而不是MD5？**
- MD5已被破解，可碰撞
- SHA256目前足够安全

**为什么不用JWT？**
- JWT无法主动撤销
- 对于管理后台，可控撤销更重要

---

## 🔧 动手练习

### 练习9.1：路径穿越攻击测试

```python
# 假设这是一个文件服务
BASE_DIR = "data"

def unsafe_read(filename: str) -> str:
    """不安全的实现"""
    with open(f"{BASE_DIR}/{filename}") as f:
        return f.read()

def safe_read(filename: str) -> str | None:
    """TODO: 实现安全版本"""
    pass

# 攻击测试
attacks = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "/etc/passwd",
    "data.txt\x00.jpg",  # NUL字节
]

for attack in attacks:
    print(f"攻击: {attack}")
    print(f"不安全: {unsafe_read(attack) if True else '文件不存在'}")
    print(f"安全: {safe_read(attack)}")
    print()
```

### 练习9.2：XSS攻击测试

```python
import html
import re

def escape_output(text: str) -> str:
    """输出转义"""
    return html.escape(text)

def sanitize_input(text: str) -> str:
    """输入过滤"""
    # TODO: 实现
    pass

# 攻击测试
attacks = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<a href=\"javascript:alert(1)\">click</a>",
]

for attack in attacks:
    print(f"原始: {attack}")
    print(f"转义: {escape_output(attack)}")
    print(f"过滤: {sanitize_input(attack)}")
    print()
```

### 练习9.3：Token安全

```python
import hashlib
import secrets

class TokenManager:
    def __init__(self):
        self.tokens = {}  # 实际应存在数据库
    
    def generate(self, user_id: str) -> str:
        """生成Token，返回明文（只显示一次）"""
        pass  # 你来实现
    
    def verify(self, token: str) -> str | None:
        """验证Token，返回user_id或None"""
        pass  # 你来实现
    
    def revoke(self, token: str) -> bool:
        """撤销Token"""
        pass  # 你来实现

# 测试
tm = TokenManager()
token = tm.generate("user123")
print(f"Token: {token}")
print(f"验证: {tm.verify(token)}")
print(f"撤销: {tm.revoke(token)}")
print(f"再次验证: {tm.verify(token)}")
```

---

## ✅ 验收标准

1. **问**：什么是路径穿越？如何防御？
   **答**：攻击者用 `../` 跳出预期目录。防御：规范化路径后检查 `is_relative_to(base_dir)`。

2. **问**：XSS是什么？如何防御？
   **答**：注入恶意JS脚本。防御：输出转义（html.escape）+ 输入过滤（移除script标签）。

3. **问**：为什么Token要存哈希而不是明文？
   **答**：数据库泄露时，攻击者拿不到有效Token。

4. **问**：双重防御原则是什么？
   **答**：输入过滤 + 输出转义，任一环节失效都有备份。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_10**: Docker基础

---

## 📝 AI Prompt（用于新对话）

```
我正在学习Web安全，当前处于阶段09：Web安全基础。

我已完成：
- 了解OWASP Top 10常见漏洞
- 理解路径穿越攻击和is_relative_to()防御
- 理解XSS攻击和html.escape()防御
- 理解Token哈希存储

请帮我：
1. 检查我对安全概念的理解是否正确
2. 评价我实现的安全函数
3. 给我一个安全场景让我分析

我的代码实现：
[粘贴练习代码]

参考项目代码：
- portal/app.py 的 safe_path() 实现路径穿越防御
- _strip_scripts() 和 _clean_str() 实现XSS防御
- gen_token() 实现Token哈希存储
```