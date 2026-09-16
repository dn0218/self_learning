# 学习阶段 06：Linux网络与端口

## 📌 阶段信息
- **阶段编号**: 06
- **前置要求**: 完成STAGE_05（Linux进程）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps / Linux系统管理员

---

## 🎯 学习目标

1. 理解TCP/UDP协议基础
2. 掌握端口的概念和查看方法
3. 理解防火墙和安全组
4. 掌握基础的网络排查命令

---

## 📚 核心概念

### 概念1：TCP连接状态

TCP连接有11种状态，最常见的是：

```
LISTEN     - 服务端等待连接
SYN_SENT   - 客户端已发送SYN，等待ACK
SYN_RCVD   - 服务端收到SYN，等待ACK
ESTABLISHED - 连接已建立（数据传输中）
FIN_WAIT_1 - 主动关闭方发送FIN
FIN_WAIT_2 - 主动关闭方等待对方FIN
TIME_WAIT  - 主动关闭方等待2MSL
CLOSE_WAIT - 被动关闭方收到FIN，等待应用关闭
LAST_ACK   - 被动关闭方发送FIN，等待ACK
```

**三次握手过程**：
```
客户端                    服务端
   │                        │
   │──── SYN ──────────────▶│  SYN_SENT → SYN_RCVD
   │                        │
   │◀─── SYN+ACK ───────────│
   │                        │
   │──── ACK ──────────────▶│  ESTABLISHED
   │                        │
```

**TIME_WAIT过多的原因**：
- 大量短连接
- 客户端频繁创建和关闭连接
- 可能导致端口耗尽

---

### 概念2：端口范围

```
0-1023      - 系统端口（需要root权限）
              22: SSH
              80: HTTP
              443: HTTPS
              3306: MySQL
              5432: PostgreSQL

1024-49151  - 注册端口（用户端口）
              3000: Node.js开发服务器
              8000: Python开发服务器
              8080: HTTP代理/Tomcat

49152-65535 - 动态端口（临时端口）
              客户端连接时临时分配
```

**查看端口占用**：
```bash
# 查看所有监听端口
ss -tlnp

# 查看特定端口
ss -tlnp | grep 80

# 查看所有连接
ss -tnp

# 输出解释
State   Recv-Q  Send-Q  Local Address  Peer Address  Process
LISTEN  0       128     0.0.0.0:80     0.0.0.0:*     users:(("nginx",pid=1234,fd=6))
```

**ss命令选项**：
```
-t: TCP
-u: UDP
-l: 只显示监听状态
-n: 数字显示端口（不解析服务名）
-p: 显示进程信息
```

---

### 概念3：防火墙

**iptables基础**：
```bash
# 查看规则
iptables -L -n

# 允许端口
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 拒绝端口
iptables -A INPUT -p tcp --dport 22 -j DROP

# 注意：iptables规则重启后失效
```

**ufw（Ubuntu简化防火墙）**：
```bash
# 启用
ufw enable

# 允许端口
ufw allow 80/tcp
ufw allow 443/tcp

# 查看状态
ufw status
```

**firewalld（CentOS/RHEL）**：
```bash
# 开放端口
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --reload

# 查看开放的端口
firewall-cmd --list-ports
```

---

### 概念4：云平台安全组

**AWS安全组**：
- 类似防火墙，但在云平台层面
- 控制入站和出站流量
- 可以引用其他安全组（如本项目）

**在本项目中（deployer.py）**：
```
EC2安全组：
  入站规则：
    来源: ALB安全组   端口: 80
    # 只允许ALB访问，不直接暴露EC2
  
  这就是"安全组引用"：
  - 不用写具体IP
  - ALB的IP变了也自动生效
```

**最佳实践**：
- 最小权限原则：只开放必需的端口
- 使用安全组引用而非具体IP
- 生产环境不要开放SSH到全网（0.0.0.0/0）

---

## 💻 项目代码参考

### 来源：modules/deployer.py - 安全组检查

```python
def ensure_aws_security_group_port80():
    """确保EC2安全组放行80端口"""
    # 这是自愈链的一部分
    # 如果80端口不通，部署会失败
    pass
```

**理解**：
- 部署前必须确保安全组正确配置
- 这是自愈设计的体现

---

### 来源：progress.txt - 你的AWS实践

```
阶段二：计算资源（EC2 + Nginx）
- 启动 EC2（t3.micro），选择 Amazon Linux 2023
- 配置安全组：放行 22（SSH）和 80（HTTP）
- 绑定弹性 IP（EIP）用于运维通道

阶段三：流量入口（ALB + 目标组）
- 安全组引用：修改 EC2 安全组，入站来源从 0.0.0.0/0 改为 ALB 安全组
```

**关键理解**：
- 安全组是AWS级别的防火墙
- 安全组引用比IP更灵活、更安全

---

## 🔧 动手练习

### 练习6.1：查看端口和连接

```bash
# 1. 查看所有TCP监听端口
ss -tlnp

# 2. 找出占用80端口的进程
ss -tlnp | grep :80

# 3. 查看当前所有TCP连接及状态
ss -tnp

# 4. 统计各状态的连接数
ss -tn | awk '{print $1}' | sort | uniq -c
```

### 练习6.2：防火墙操作（根据系统选择）

**Ubuntu/ufw**：
```bash
# 查看状态
sudo ufw status

# 如果未启用，先允许SSH（重要！）
sudo ufw allow 22/tcp

# 启用
sudo ufw enable

# 允许HTTP
sudo ufw allow 80/tcp

# 再次查看
sudo ufw status
```

**CentOS/firewalld**：
```bash
# 查看状态
sudo firewall-cmd --state

# 开放端口
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --add-port=22/tcp --permanent

# 重载
sudo firewall-cmd --reload

# 查看
sudo firewall-cmd --list-ports
```

### 练习6.3：网络排查

**场景**：Web服务无法访问

```bash
# 步骤1：检查服务是否运行
ps aux | grep nginx

# 步骤2：检查端口是否监听
ss -tlnp | grep 80

# 步骤3：检查防火墙
sudo ufw status  # 或 firewall-cmd --list-ports

# 步骤4：本地测试
curl http://localhost

# 步骤5：外部测试（如果本地正常）
curl http://服务器IP

# 步骤6：如果外部不通，检查安全组（云服务器）
```

---

## ✅ 验收标准

1. **问**：ss命令的-tlnp选项分别是什么意思？
   **答**：-t=TCP, -l=只显示监听, -n=数字显示端口, -p=显示进程信息

2. **问**：安全组引用比IP地址有什么优势？
   **答**：不需要维护具体IP列表，IP变化时自动生效，更安全更灵活。

3. **问**：如何判断端口是否被占用？
   **答**：`ss -tlnp | grep 端口号`，如果有输出则被占用。

4. **问**：本地curl正常但外部访问不了，可能是什么原因？
   **答**：防火墙或安全组没开放端口。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_07**: DNS原理与Cloudflare

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段06：Linux网络与端口。

我已完成：
- 理解TCP连接状态（LISTEN/ESTABLISHED/TIME_WAIT等）
- 掌握端口范围和ss命令使用
- 理解防火墙和安全组的作用
- 掌握基础网络排查步骤

请帮我：
1. 确认我对网络概念的理解是否正确
2. 给我一个故障场景让我分析

我的系统输出：
[粘贴 ss -tlnp 和防火墙状态的输出]

参考项目代码：
- deployer.py 有 ensure_aws_security_group_port80 自愈检查
- 本项目使用AWS安全组引用（EC2来源设为ALB安全组）
```