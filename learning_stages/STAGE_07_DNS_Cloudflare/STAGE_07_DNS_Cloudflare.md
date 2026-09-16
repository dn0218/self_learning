# 学习阶段 07：DNS原理与Cloudflare

## 📌 阶段信息
- **阶段编号**: 07
- **前置要求**: 完成STAGE_06（Linux网络）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解DNS的工作原理
2. 掌握A记录、CNAME、TTL等概念
3. 理解Cloudflare代理模式
4. 掌握DNS排查命令

---

## 📚 核心概念

### 概念1：DNS解析过程

```
用户浏览器
    │
    ▼
本地DNS缓存（浏览器/操作系统）
    │ 未命中
    ▼
本地DNS服务器（ISP提供）
    │ 未命中
    ▼
根域名服务器（.）
    │ 返回：去问 .com 的服务器
    ▼
顶级域名服务器（.com）
    │ 返回：去问 example.com 的服务器
    ▼
权威域名服务器（example.com）
    │ 返回：IP地址 1.2.3.4
    ▼
本地DNS缓存结果
    │
    ▼
浏览器访问 1.2.3.4
```

**关键理解**：
- DNS是分层结构：根 → 顶级域 → 二级域
- 每级都有缓存，不是每次都完整查询
- TTL决定缓存时间

---

### 概念2：DNS记录类型

```
A记录      - 域名 → IPv4地址
             example.com → 1.2.3.4

AAAA记录   - 域名 → IPv6地址
             example.com → 2001:db8::1

CNAME      - 域名 → 另一个域名
             www.example.com → example.com

MX记录     - 邮件服务器
             @ → mail.example.com

TXT记录    - 文本信息（SPF/DKIM验证等）
             @ → "v=spf1 include:_spf.google.com ~all"

NS记录     - 域名服务器
             example.com → ns1.cloudflare.com
```

**A记录 vs CNAME**：
```
# A记录：直接指向IP
example.com  A      1.2.3.4

# CNAME：指向另一个域名
www.example.com  CNAME  example.com

# CNAME的好处：
# 如果example.com的IP变了，只需改A记录
# www会自动跟着变
```

---

### 概念3：TTL（Time To Live）

```
TTL = 300   → 缓存5分钟
TTL = 3600  → 缓存1小时
TTL = 86400 → 缓存1天
```

**生产环境建议**：
- 稳定服务：TTL 3600-86400
- 即将变更：TTL 300（提前改，等缓存过期）
- 容灾切换：TTL 60-300

**陷阱**：
- TTL不是精确的，各DNS服务器可能不遵守
- 变更DNS后，可能需要等TTL时间才能全球生效

---

### 概念4：Cloudflare代理模式

```
Cloudflare DNS设置页面：
┌─────────────────────────────────────────┐
│ 类型  名称      内容         代理状态    │
│ A     @        1.2.3.4      [已代理]    │ ← 橙色云朵
│ A     www      1.2.3.4      [仅DNS]     │ ← 灰色云朵
└─────────────────────────────────────────┘
```

**已代理（橙色云朵）**：
```
用户 ──▶ Cloudflare CDN ──▶ 你的服务器
        (隐藏真实IP)
        (DDoS防护)
        (SSL自动配置)
        (缓存静态资源)
```

**仅DNS（灰色云朵）**：
```
用户 ──▶ 你的服务器（直接访问）
        真实IP暴露
        无额外保护
```

**本项目使用**：
- deployer.py 使用已代理模式
- 隐藏EC2真实IP
- 自动获得SSL证书

---

## 💻 项目代码参考

### 来源：modules/deployer.py - DNS客户端

```python
class CloudflareDNSClient:
    BASE = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: str, zone_id: str, domain: str):
        self.zone_id = zone_id
        self.domain = domain
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
        })
    
    def get_a_record(self, name: str = None) -> Optional[dict]:
        """获取A记录"""
        result = self._request("GET", "/dns_records",
                               params={"type": "A", "name": name})
        # 返回 {id, name, content, proxied}
        return result
    
    def upsert_a_record(self, ip: str, name: str = None, 
                        proxied: bool = True) -> tuple[str, str]:
        """
        幂等更新A记录
        返回 (动作, record_id)
        动作: "created" | "updated" | "unchanged"
        """
        rec = self.get_a_record(name)
        if rec is None:
            # 创建新记录
            return self._request("POST", "/dns_records", json={
                "type": "A", "name": name, "content": ip, "proxied": proxied
            })
        if rec["content"] != ip:
            # IP变了，更新
            return self._request("PUT", f"/dns_records/{rec['id']}", json={
                "type": "A", "name": name, "content": ip, "proxied": proxied
            })
        # 无变化
        return "unchanged", rec["id"]
```

**理解要点**：
- 使用Cloudflare API管理DNS
- 幂等设计：多次执行结果相同
- `proxied=True` 启用代理模式

---

### 来源：modules/deployer.py - SSL设置

```python
def ensure_ssl_mode(self) -> bool:
    """确保SSL模式为flexible（CF终结SSL，源站HTTP）"""
    current = self.get_ssl_mode()
    if current != "flexible":
        return self.set_ssl_mode("flexible")
    return True
```

**SSL模式解释**：
```
Flexible:   用户──HTTPS──▶CF──HTTP──▶源站（源站无需证书）
Full:       用户──HTTPS──▶CF──HTTPS──▶源站（源站需自签名证书）
Full(Strict): 用户──HTTPS──▶CF──HTTPS──▶源站（源站需有效证书）
```

**本项目用Flexible**：
- EC2运行HTTP（80端口）
- Cloudflare终结SSL
- 用户看到HTTPS，但CF到源站是HTTP

---

## 🔧 动手练习

### 练习7.1：DNS查询

```bash
# 使用dig查询
dig example.com

# 输出解释
;; QUESTION SECTION:
;example.com.           IN  A          # 查询类型

;; ANSWER SECTION:
example.com.        86400   IN  A   93.184.216.34
# 域名           TTL    类型  IP地址

# 只显示答案
dig +short example.com

# 查询特定记录类型
dig example.com MX
dig example.com NS
dig example.com TXT
```

### 练习7.2：DNS追踪

```bash
# 追踪完整解析过程
dig +trace example.com

# 输出解释
.                       518400  IN  NS  a.root-servers.net.
# 根服务器

com.                    172800  IN  NS  a.gtld-servers.net.
# .com服务器

example.com.            172800  IN  NS  ns.icann.org.
# example.com的权威服务器

example.com.            86400   IN  A   93.184.216.34
# 最终IP
```

### 练习7.3：DNS排查

**场景**：域名无法访问

```bash
# 步骤1：检查DNS是否解析
dig yourdomain.com
# 如果没有ANSWER SECTION，DNS配置有问题

# 步骤2：检查是否指向正确IP
dig +short yourdomain.com
# 对比预期IP

# 步骤3：检查Cloudflare代理状态
# 登录Cloudflare面板查看

# 步骤4：检查是否被拦截
curl -I https://yourdomain.com
# 如果返回522/521，源站不可达
```

---

## ✅ 验收标准

1. **问**：A记录和CNAME有什么区别？
   **答**：A记录直接指向IP，CNAME指向另一个域名。CNAME的好处是IP变了只需改一条A记录。

2. **问**：TTL是什么？为什么要设置低TTL？
   **答**：TTL是DNS缓存时间。低TTL可以在变更DNS后更快生效，但会增加DNS查询量。

3. **问**：Cloudflare代理模式有什么好处？
   **答**：隐藏真实IP、DDoS防护、自动SSL、全球CDN加速。

4. **问**：dig +trace命令显示什么？
   **答**：显示完整的DNS解析路径，从根服务器到权威服务器。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_08**: 幂等性与自愈设计

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段07：DNS原理与Cloudflare。

我已完成：
- 理解DNS分层解析过程
- 掌握A记录、CNAME、TTL概念
- 理解Cloudflare代理模式（橙色云朵）
- 掌握dig命令进行DNS排查

请帮我：
1. 确认我对DNS概念的理解是否正确
2. 给我一个DNS故障场景让我分析

我的DNS查询结果：
[粘贴 dig yourdomain.com 的输出]

参考项目代码：
- modules/deployer.py 实现了 CloudflareDNSClient
- upsert_a_record 是幂等的DNS更新
- 使用 proxied=True 启用代理模式
- SSL模式设为 flexible（CF终结SSL，源站HTTP）
```