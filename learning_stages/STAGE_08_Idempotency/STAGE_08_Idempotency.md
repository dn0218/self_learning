# 学习阶段 08：幂等性与自愈设计

## 📌 阶段信息
- **阶段编号**: 08
- **前置要求**: 完成STAGE_07（DNS）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解幂等性的概念和重要性
2. 掌握自愈设计的核心思想
3. 理解本项目deployer.py的5阶段自愈链
4. 能够设计简单的幂等操作

---

## 📚 核心概念

### 概念1：什么是幂等性？

**定义**：多次执行相同操作，结果相同。

**生活中的例子**：
```
幂等操作：
- 电梯按钮：按100次，电梯只来一次
- 开关灯：开100次，灯还是开着

非幂等操作：
- ATM取钱：取100次，钱没了
- 发邮件：发100次，收件人收到100封
```

**编程中的幂等**：
```python
# 非幂等：每次调用都创建新记录
def create_user(name):
    db.insert("INSERT INTO users (name) VALUES (?)", name)

# 幂等：存在则跳过，不存在才创建
def ensure_user(name):
    existing = db.query("SELECT * FROM users WHERE name = ?", name)
    if existing:
        return existing  # 已存在，不重复创建
    db.insert("INSERT INTO users (name) VALUES (?)", name)
    return db.query("SELECT * FROM users WHERE name = ?", name)
```

---

### 概念2：为什么幂等性重要？

**场景1：网络重试**
```
客户端 ──请求──▶ 服务端
        （超时）
客户端 ──重试──▶ 服务端

# 如果是非幂等：
# - 创建了2条记录
# - 扣了2次钱

# 如果是幂等：
# - 第2次请求检测到已存在
# - 直接返回，不重复执行
```

**场景2：自动化脚本**
```bash
# 非幂等脚本：每次运行都创建新资源
python deploy.py  # 创建EC2
python deploy.py  # 又创建一个EC2！
python deploy.py  # 又一个！

# 幂等脚本：资源存在就跳过
python deploy.py  # 创建EC2
python deploy.py  # 检测到已存在，跳过
python deploy.py  # 跳过
```

**SRE原则**：所有自动化脚本都必须幂等！

---

### 概念3：自愈设计

**自愈（Self-healing）**：检测问题并自动修复。

```
传统运维：
监控发现故障 → 告警 → 人工处理 → 恢复
时间：可能几十分钟

自愈设计：
监控发现故障 → 自动修复 → 恢复
时间：几秒到几分钟
```

**本项目的自愈链**：
```
部署开始
    │
    ▼
S0: 配置检查 ──失败──▶ 记录问题，继续
    │
    ▼
S1: 安全组检查 ──失败──▶ 尝试自动修复/提示
    │
    ▼
S2: SSL设置 ──失败──▶ 尝试设置
    │
    ▼
S3: DNS同步 ──发现漂移──▶ 自动修复
    │
    ▼
S4: 目录创建 ──不存在──▶ 自动创建
    │
    ▼
主部署流程
```

**关键思想**：
- 每个阶段独立检查
- 发现问题尝试修复
- 修复失败记录问题，不阻塞
- 下次运行可能已修复

---

## 💻 项目代码参考

### 来源：modules/deployer.py - 自愈链

```python
def run(self):
    """主入口：运行自愈链 + 部署"""
    
    # 自愈链（任一失败不阻塞）
    self.s0_config_check()           # 配置校验
    self.s1_ensure_security_group()  # 80端口可达性
    self.s2_ensure_ssl_mode()        # SSL设置
    self.s3_sync_dns()               # DNS同步
    self.s4_ensure_remote_dir()      # 目录创建
    
    # 主部署
    self.deploy_all()
```

**每个阶段的职责**：

| 阶段 | 检查什么 | 自愈动作 |
|-----|---------|---------|
| S0 | 配置文件有效性 | 无（配置错误需人工修复） |
| S1 | EC2安全组是否放行80 | 提示如何修复 |
| S2 | Cloudflare SSL模式 | 自动设置为flexible |
| S3 | DNS是否指向正确IP | 自动更新A记录 |
| S4 | 远程目录是否存在 | SSH创建目录 |

---

### 来源：modules/deployer.py - DNS自愈

```python
def s3_sync_dns(self):
    """同步DNS记录，修复漂移"""
    
    # 获取当前DNS记录
    rec = self.cf.get_a_record(self.domain)
    
    if rec is None:
        # 记录不存在，创建
        action, _ = self.cf.upsert_a_record(self.ec2_ip)
        print(f"DNS: 创建记录 → {self.ec2_ip}")
        return
    
    if rec["content"] != self.ec2_ip:
        # IP不一致（漂移），修复
        action, _ = self.cf.upsert_a_record(self.ec2_ip)
        print(f"DNS: 检测到漂移，已修复 {rec['content']} → {self.ec2_ip}")
        return
    
    print(f"DNS: 正常，指向 {self.ec2_ip}")
```

**什么情况下会漂移？**
- EC2更换了EIP
- 手动修改了DNS记录
- 其他脚本修改了DNS

**自愈的好处**：
- 无需人工干预
- 定期运行即可保证一致性
- 是"GitOps"思想的体现

---

## 🔧 动手练习

### 练习8.1：理解幂等性

分析以下函数是否幂等：

```python
# 函数A
def send_email(to, subject, body):
    smtp.send(to, subject, body)

# 函数B
def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

# 函数C
def ensure_file(path, content):
    if os.path.exists(path):
        with open(path) as f:
            if f.read() == content:
                return  # 已存在且内容正确
    with open(path, 'w') as f:
        f.write(content)

# 问题：
# 1. 哪个是幂等的？
# 2. 如何让函数A幂等？
```

### 练习8.2：设计幂等函数

```python
# TODO: 实现幂等的用户创建函数
def ensure_user(db, username, email):
    """
    确保用户存在
    - 不存在：创建
    - 已存在：检查email是否一致，不一致则更新
    - 返回用户对象
    """
    pass  # 你来实现
```

### 练习8.3：设计自愈检查

```python
# TODO: 实现一个简单的自愈检查
class ServiceHealthChecker:
    def __init__(self, url: str):
        self.url = url
    
    def check(self) -> bool:
        """检查服务是否健康"""
        pass  # 你来实现
    
    def heal(self) -> bool:
        """尝试自愈"""
        pass  # 你来实现
    
    def check_and_heal(self):
        """检查并自愈"""
        if self.check():
            print("服务正常")
            return True
        
        print("服务异常，尝试自愈...")
        if self.heal():
            print("自愈成功")
            return self.check()
        
        print("自愈失败")
        return False

# 测试
checker = ServiceHealthChecker("http://localhost:8080/health")
checker.check_and_heal()
```

---

## ✅ 验收标准

1. **问**：什么是幂等性？为什么在自动化脚本中重要？
   **答**：幂等性指多次执行结果相同。在自动化脚本中重要因为：网络可能超时需要重试、脚本可能被多次运行、避免重复创建资源。

2. **问**：deployer.py的5阶段自愈链分别做什么？
   **答**：S0配置检查、S1安全组检查、S2 SSL设置、S3 DNS同步、S4目录创建。每个阶段发现问题尝试修复。

3. **问**：DNS漂移是什么？如何自愈？
   **答**：DNS记录指向了错误的IP。自愈方式：对比期望IP和实际IP，不一致则更新。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_09**: Web安全基础

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段08：幂等性与自愈设计。

我已完成：
- 理解幂等性的定义和重要性
- 理解为什么自动化脚本必须幂等
- 掌握自愈设计的核心思想
- 理解deployer.py的5阶段自愈链

请帮我：
1. 检查我对幂等性概念的理解是否正确
2. 评价我设计的幂等函数
3. 给我一个场景让我设计自愈逻辑

我实现的代码：
[粘贴练习代码]

参考项目代码：
- modules/deployer.py 的 run() 方法实现自愈链
- s3_sync_dns() 实现DNS漂移自愈
- upsert_a_record() 是幂等的DNS更新
```