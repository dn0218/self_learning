# 学习阶段 12：监控与告警

## 📌 阶段信息
- **阶段编号**: 12
- **前置要求**: 完成STAGE_11（Kubernetes）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解RED和USE监控方法论
2. 理解Prometheus + Grafana架构
3. 掌握基础监控指标类型
4. 能够设计简单的告警规则

---

## 📚 核心概念

### 概念1：监控方法论

**RED方法（适用于请求驱动服务）**：
```
R - Rate (请求速率)
    每秒请求数 (QPS/RPS)
    
E - Errors (错误率)
    失败请求比例
    
D - Duration (响应时间)
    P50/P95/P99 延迟
```

**USE方法（适用于资源）**：
```
U - Utilization (使用率)
    CPU使用率、内存使用率
    
S - Saturation (饱和度)
    运行队列长度、IO等待
    
E - Errors (错误率)
    网络丢包、磁盘错误
```

**应用示例**：
```
对于Web服务（用RED）：
- 请求量是否正常？
- 错误率是否超过阈值？
- 响应时间是否变慢？

对于服务器（用USE）：
- CPU使用率是否过高？
- 内存是否快用完？
- 磁盘IO是否饱和？
```

---

### 概念2：Prometheus架构

```
┌─────────────────────────────────────────────────────────┐
│                    Prometheus                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │Retrieval│  │  TSDB   │  │  Rules  │                │
│  │ 拉取指标 │  │ 时序存储 │  │ 告警规则 │                │
│  └─────────┘  └─────────┘  └─────────┘                │
└─────────────────────────────────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Exporter │   │ Grafana  │   │Alertmgr  │
│ 暴露指标 │   │  可视化  │   │  告警    │
└──────────┘   └──────────┘   └──────────┘
```

**Prometheus核心特点**：
- Pull模式：主动拉取指标（ exporter暴露的/metrics端点）
- 时序数据库：存储带时间戳的指标
- PromQL：强大的查询语言

---

### 概念3：指标类型

```python
# Counter - 只增计数器
# 用途：请求数、错误数
requests_total{method="GET"} 100
requests_total{method="GET"} 105  # +5

# Gauge - 可增可减
# 用途：当前连接数、内存使用
memory_bytes 1024000
memory_bytes 1010000  # 可以减少

# Histogram - 直方图
# 用途：响应时间分布
http_request_duration_seconds_bucket{le="0.1"} 100
http_request_duration_seconds_bucket{le="0.5"} 150
http_request_duration_seconds_bucket{le="1.0"} 180

# 计算 P99: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

**为本项目添加指标**：
```python
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# 自动添加的指标：
# - flask_http_request_total (Counter)
# - flask_http_request_duration_seconds (Histogram)
# - flask_http_request_exceptions_total (Counter)

# 访问 /metrics 端点获取Prometheus格式指标
```

---

### 概念4：告警规则

```yaml
# alert_rules.yml
groups:
- name: kl-agent-alerts
  rules:
  # 错误率告警
  - alert: HighErrorRate
    expr: rate(flask_http_request_total{status="500"}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "高错误率"
      description: "5xx错误率超过10%"
  
  # 响应时间告警
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "高延迟"
      description: "P99响应时间超过1秒"
  
  # 资源告警
  - alert: HighMemory
    expr: process_resident_memory_bytes / 1024 / 1024 > 500
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用过高"
      description: "进程内存超过500MB"
```

---

## 💻 项目代码参考

### 为portal/app.py添加Prometheus指标

```python
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask

app = Flask(__name__)

# 初始化Prometheus指标
metrics = PrometheusMetrics(app)

# 自定义指标
from prometheus_client import Counter, Histogram, Gauge

# 请求计数器
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'method']
)

# 响应时间
api_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint']
)

# 当前活跃连接
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# 在路由中使用
@app.route('/api/publish')
def publish():
    api_requests.labels(endpoint='publish', method='POST').inc()
    with api_duration.labels(endpoint='publish').time():
        # ... 业务逻辑
        pass
    return {'status': 'ok'}
```

---

## 🔧 动手练习

### 练习12.1：部署Prometheus + Grafana

```bash
# 使用docker-compose
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'flask-app'
    static_configs:
      - targets: ['host.docker.internal:8787']

# 启动
docker-compose up -d

# 访问
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

### 练习12.2：查询PromQL

```promql
# 查询请求速率
rate(flask_http_request_total[5m])

# 查询错误率
sum(rate(flask_http_request_total{status=~"5.."}[5m])) 
/ sum(rate(flask_http_request_total[5m]))

# 查询P99响应时间
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# 查询内存使用
process_resident_memory_bytes / 1024 / 1024
```

### 练习12.3：创建Grafana仪表板

```
1. 登录Grafana (localhost:3000)
2. 添加数据源 → Prometheus → localhost:9090
3. 创建Dashboard
4. 添加Panel：
   - 请求速率: rate(flask_http_request_total[5m])
   - 错误率: sum(rate(...{status=~"5.."}[5m]))
   - 响应时间: histogram_quantile(0.99, ...)
5. 保存Dashboard
```

---

## ✅ 验收标准

1. **问**：RED和USE方法分别用于什么？
   **答**：RED用于请求驱动服务（Rate/Errors/Duration），USE用于资源监控（Utilization/Saturation/Errors）。

2. **问**：Counter和Gauge有什么区别？
   **答**：Counter只增不减（请求数、错误数），Gauge可增可减（当前连接数、内存）。

3. **问**：Prometheus如何获取指标？
   **答**：Pull模式，主动访问应用的/metrics端点拉取指标。

4. **问**：告警规则的`for: 5m`是什么意思？
   **答**：条件持续5分钟才触发告警，避免瞬时波动误报。

---

## 🔗 学习总结

恭喜完成全部12个阶段！

**你的技术栈**：
```
HTTP/网络      ✓ STAGE 01-02
AI工程         ✓ STAGE 03-04
Linux运维      ✓ STAGE 05-06
云服务/DNS     ✓ STAGE 07
自动化/SRE思维 ✓ STAGE 08
安全           ✓ STAGE 09
容器化         ✓ STAGE 10-11
监控           ✓ STAGE 12
```

**下一步建议**：
1. 复习所有阶段，确保每个概念都理解
2. 完成所有练习，动手实践
3. 阅读 `INTERVIEW_QA_HANDBOOK.md` 准备面试
4. 用这个项目作为面试作品

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段12：监控与告警。

我已完成全部12个阶段：
- HTTP基础与重试机制
- OpenAI SDK与Prompt工程
- Linux进程与网络
- DNS与Cloudflare
- 幂等性与自愈设计
- Web安全
- Docker与Kubernetes
- 监控与告警

请帮我：
1. 检查我的监控配置是否合理
2. 给我一个综合练习巩固所有知识
3. 模拟面试，问我SRE相关问题

我的监控配置：
[粘贴你的Prometheus配置]

参考项目代码：
- 本项目 portal/app.py 可添加Prometheus指标
- pipeline.py 的 healthcheck 是监控的一部分
- deployer.py 的自愈链体现了SRE思维
```