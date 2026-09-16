# 学习阶段 11：Kubernetes基础

## 📌 阶段信息
- **阶段编号**: 11
- **前置要求**: 完成STAGE_10（Docker基础）
- **预计时间**: 3-4天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解Kubernetes的核心概念
2. 掌握Pod、Deployment、Service的基本使用
3. 理解K8s的自愈和滚动更新机制
4. 能够部署简单的应用到K8s

---

## 📚 核心概念

### 概念1：Kubernetes是什么？

**K8s解决的问题**：
```
单机Docker：
- 容器挂了，需要手动重启
- 机器挂了，服务全挂
- 流量突增，需要手动扩容

Kubernetes集群：
- 容器挂了，自动重启
- 节点挂了，自动迁移到其他节点
- 流量突增，自动扩容副本数
```

**核心组件**：
```
┌─────────────────────────────────────────────────────┐
│                    Master Node                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ API Srv  │ │Scheduler │ │Controller│            │
│  └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   Worker Node   │  │   Worker Node   │
│ ┌────┐ ┌────┐  │  │ ┌────┐ ┌────┐  │
│ │Pod │ │Pod │  │  │ │Pod │ │Pod │  │
│ └────┘ └────┘  │  │ └────┘ └────┘  │
│   Kubelet       │  │   Kubelet       │
└─────────────────┘  └─────────────────┘
```

---

### 概念2：核心对象

**Pod - 最小调度单位**：
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: my-app:v1
    ports:
    - containerPort: 8080
```

**为什么需要Pod而不是直接管理容器？**
- 一个Pod可以包含多个容器（边车模式）
- Pod内容器共享网络和存储
- 是K8s调度的最小单位

**Deployment - 管理Pod副本**：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3              # 3个副本
  selector:
    matchLabels:
      app: my-app
  template:                # Pod模板
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: my-app:v1
        ports:
        - containerPort: 8080
```

**Deployment的能力**：
- 维持指定副本数（Pod挂了自动重建）
- 滚动更新（逐步替换旧Pod）
- 回滚（出问题可以回退版本）

**Service - 提供稳定访问入口**：
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  type: LoadBalancer       # 对外暴露
  selector:
    app: my-app
  ports:
  - port: 80               # Service端口
    targetPort: 8080       # Pod端口
```

**Service的类型**：
```
ClusterIP    - 只在集群内部可访问（默认）
NodePort     - 通过节点IP:端口访问
LoadBalancer - 创建云负载均衡器（AWS ALB等）
```

---

### 概念3：自愈机制

```
场景1：容器崩溃
K8s检测到容器退出 → 根据restartPolicy重启

场景2：健康检查失败
readinessProbe失败 → 从Service摘除
livenessProbe失败 → 重启容器

场景3：节点故障
节点失联 → 调度器在其他节点重建Pod

场景4：手动删除Pod
Deployment控制器检测到副本数不足 → 创建新Pod
```

---

### 概念4：常用命令

```bash
# ========== 查看资源 ==========
kubectl get pods                    # 查看Pod
kubectl get deployments             # 查看Deployment
kubectl get services                # 查看Service
kubectl get all                     # 查看所有资源

# ========== 描述资源 ==========
kubectl describe pod <pod-name>     # Pod详情
kubectl logs <pod-name>             # 查看日志
kubectl logs -f <pod-name>          # 实时日志

# ========== 创建/更新 ==========
kubectl apply -f deployment.yaml    # 应用配置
kubectl delete -f deployment.yaml   # 删除资源

# ========== 扩缩容 ==========
kubectl scale deployment my-app --replicas=5

# ========== 滚动更新 ==========
kubectl set image deployment/my-app app=my-app:v2
kubectl rollout status deployment/my-app    # 查看状态
kubectl rollout undo deployment/my-app      # 回滚

# ========== 进入容器 ==========
kubectl exec -it <pod-name> -- bash
```

---

## 💻 项目代码参考

### 为本项目创建K8s配置

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kl-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: kl-agent
  template:
    metadata:
      labels:
        app: kl-agent
    spec:
      containers:
      - name: app
        image: kl-agent:v1
        ports:
        - containerPort: 8787
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /
            port: 8787
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8787
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: config
          mountPath: /app/config.json
          subPath: config.json
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: kl-agent-data
      - name: config
        configMap:
          name: kl-agent-config
---
apiVersion: v1
kind: Service
metadata:
  name: kl-agent-svc
spec:
  type: LoadBalancer
  selector:
    app: kl-agent
  ports:
  - port: 80
    targetPort: 8787
```

---

## 🔧 动手练习

### 练习11.1：使用minikube本地K8s

```bash
# 安装minikube（本地K8s）
# Windows: choco install minikube
# Mac: brew install minikube
# Linux: 参考官方文档

# 启动集群
minikube start

# 查看状态
kubectl cluster-info
kubectl get nodes

# 部署一个示例应用
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --type=NodePort --port=80

# 访问应用
minikube service nginx

# 清理
kubectl delete deployment nginx
kubectl delete service nginx
```

### 练习11.2：部署本项目到K8s

```bash
# 1. 构建镜像（先让minikube使用本地Docker）
eval $(minikube docker-env)
docker build -t kl-agent:v1 .

# 2. 创建Namespace
kubectl create namespace kl-agent

# 3. 应用配置
kubectl apply -f deployment.yaml -n kl-agent

# 4. 查看状态
kubectl get all -n kl-agent

# 5. 查看Pod日志
kubectl logs -f deployment/kl-agent -n kl-agent

# 6. 扩容测试
kubectl scale deployment kl-agent --replicas=3 -n kl-agent
kubectl get pods -n kl-agent

# 7. 清理
kubectl delete namespace kl-agent
```

### 练习11.3：模拟故障自愈

```bash
# 1. 部署应用
kubectl apply -f deployment.yaml

# 2. 找到一个Pod
kubectl get pods

# 3. 手动删除Pod
kubectl delete pod <pod-name>

# 4. 立即查看，Pod正在重建
kubectl get pods

# 5. 几秒后，新Pod运行
kubectl get pods
```

---

## ✅ 验收标准

1. **问**：Pod和容器有什么区别？
   **答**：Pod是K8s最小调度单位，可以包含1个或多个容器。Pod内容器共享网络和存储。

2. **问**：Deployment的作用是什么？
   **答**：管理Pod副本数、滚动更新、回滚、自愈。

3. **问**：Service的作用是什么？
   **答**：提供稳定的访问入口，负载均衡到后端Pod。

4. **问**：删除Pod后会发生什么？
   **答**：Deployment控制器检测到副本数不足，自动创建新Pod。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_12**: 监控与告警

---

## 📝 AI Prompt（用于新对话）

```
我正在学习Kubernetes，当前处于阶段11：Kubernetes基础。

我已完成：
- 理解K8s核心概念（Pod/Deployment/Service）
- 理解K8s自愈机制
- 掌握基本kubectl命令
- 能够部署简单应用到K8s

请帮我：
1. 检查我的K8s配置文件是否正确
2. 解释一些K8s概念
3. 给我一个K8s实践练习

我的deployment.yaml：
[粘贴你的配置]

参考项目代码：
- 本项目可用Docker构建镜像
- 然后部署到K8s集群
- 使用Deployment管理副本数
- 使用Service暴露服务
```