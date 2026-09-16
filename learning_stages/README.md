# SRE/DevOps 技术学习路径

> 基于kl_restaurant_agent项目实战经验的系统性学习计划

---

## 📋 学习阶段总览

| 阶段 | 主题 | 核心技能 | 预计时间 |
|------|------|----------|----------|
| 01 | HTTP基础 | 协议理解、状态码、请求头 | 1天 |
| 02 | HTTP重试机制 | 指数退避、熔断器、超时处理 | 2天 |
| 03 | OpenAI SDK | LLM API调用、参数调优 | 1天 |
| 04 | Prompt工程 | 设计原则、Few-shot、输出控制 | 1天 |
| 05 | Linux进程 | 进程状态、Load Average、系统监控 | 2天 |
| 06 | Linux网络 | 端口管理、防火墙、安全组 | 2天 |
| 07 | DNS与Cloudflare | 域名解析、CDN、代理模式 | 1天 |
| 08 | 幂等性与自愈 | 幂等设计、自动化修复 | 2天 |
| 09 | Web安全 | OWASP Top 10、常见漏洞防御 | 2天 |
| 10 | Docker基础 | 容器化、镜像构建、Dockerfile | 2天 |
| 11 | Kubernetes基础 | Pod/Deployment/Service | 2天 |
| 12 | 监控系统 | Prometheus、指标类型、告警 | 2天 |
| 13 | CI/CD Pipeline | GitHub Actions、自动化部署 | 2天 |

**总计**：约20天（每天2-3小时）

---

## 🎯 学习目标

完成全部阶段后，你将能够：

1. **理解HTTP协议**：状态码、请求头、重试策略
2. **调用LLM API**：OpenAI SDK使用、Prompt设计
3. **管理Linux系统**：进程监控、网络排查、防火墙配置
4. **配置DNS/CDN**：Cloudflare管理、域名解析
5. **设计可靠系统**：幂等性、自愈机制、安全防御
6. **容器化部署**：Docker镜像构建、Kubernetes编排
7. **监控系统**：Prometheus指标、告警配置
8. **自动化CI/CD**：GitHub Actions配置、自动部署

---

## 📚 学习方法

### 每个阶段的结构

```
learning_stages/
├── STAGE_XX_Name/
│   ├── STAGE_XX_Name.md    # 详细学习内容
│   └── INSTRUCTOR.md        # 学习指导员System Prompt
```

### 学习流程

```
1. 阅读 STAGE_XX_Name.md 理解概念
2. 完成动手练习
3. 开启新对话，粘贴INSTRUCTOR.md内容作为指导
4. 让指导员检查你的理解和代码
5. 通过验收后进入下一阶段
```

### 使用AI指导员

每次开始新阶段时，在新对话中：

```
我正在学习[阶段名称]，当前处于阶段XX。

请作为我的学习指导员，帮我：
1. 检查我的理解是否正确
2. 回答我的疑问
3. 给我练习任务
```

---

## 🗺️ 推荐学习路径

### 路径A：SRE工程师
```
01 → 02 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13
HTTP → 重试 → Linux → 网络 → DNS → 幂等 → 安全 → Docker → K8s → 监控 → CI/CD
```

### 路径B：AI Infra工程师
```
01 → 02 → 03 → 04 → 10 → 11 → 12 → 13
HTTP → 重试 → SDK → Prompt → Docker → K8s → 监控 → CI/CD
```

### 路径C：DevOps工程师
```
01 → 02 → 05 → 06 → 10 → 11 → 12 → 13
HTTP → 重试 → Linux → 网络 → Docker → K8s → 监控 → CI/CD
```

---

## 🔗 项目关联

本学习路径基于实际项目 `kl_restaurant_agent` 提炼：

| 阶段 | 项目代码参考 |
|------|-------------|
| 01-02 | modules/scraper.py, modules/deployer.py |
| 03-04 | modules/builder.py |
| 05-06 | 生产环境运维经验 |
| 07 | modules/deployer.py (DNS操作) |
| 08 | modules/deployer.py (自愈链) |
| 09 | portal/app.py (安全防御) |
| 10-11 | container/ 目录（Docker/K8s） |
| 12 | 监控配置文件 |
| 13 | .github/workflows/ |

---

## ✅ 进度追踪

在每个阶段完成后，标记进度：

- [ ] Stage 01: HTTP基础
- [ ] Stage 02: HTTP重试机制
- [ ] Stage 03: OpenAI SDK
- [ ] Stage 04: Prompt工程
- [ ] Stage 05: Linux进程
- [ ] Stage 06: Linux网络
- [ ] Stage 07: DNS与Cloudflare
- [ ] Stage 08: 幂等性与自愈
- [ ] Stage 09: Web安全
- [ ] Stage 10: Docker基础
- [ ] Stage 11: Kubernetes基础
- [ ] Stage 12: 监控系统
- [ ] Stage 13: CI/CD Pipeline

---

## 💡 学习建议

1. **不要跳过基础**：HTTP和重试是所有后续内容的基础
2. **动手实践**：每个练习都要亲手写代码
3. **关联项目**：理解本项目的实际应用场景
4. **记录笔记**：在阶段文件中添加你的理解
5. **多设备同步**：推送到GitHub，随时随地学习

---

## 🚀 开始学习

```bash
# 克隆仓库（假设你已推送到GitHub）
git clone https://github.com/YOUR_USERNAME/self_learning.git

# 进入阶段目录
cd self_learning/learning_stages/STAGE_01_HTTP_Basics

# 开始学习
# 阅读 STAGE_01_HTTP_Basics.md
```

祝学习顺利！每一步都是通往SRE/DevOps工程师的基石。