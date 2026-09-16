# 学习阶段 10：Docker基础

## 📌 阶段信息
- **阶段编号**: 10
- **前置要求**: 完成STAGE_09（Web安全）
- **预计时间**: 3-4天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解Docker的核心概念（镜像/容器/仓库）
2. 掌握Dockerfile的基本编写
3. 理解镜像分层原理
4. 掌握常用Docker命令

---

## 📚 核心概念

### 概念1：Docker是什么？

**Docker vs 虚拟机**：
```
虚拟机：
┌────────────────────────────────────────────┐
│ App A │ App B │ App C                      │
│ Guest OS │ Guest OS │ Guest OS            │
├────────────────────────────────────────────┤
│            Hypervisor                       │
├────────────────────────────────────────────┤
│            Host OS                          │
├────────────────────────────────────────────┤
│            物理硬件                          │
└────────────────────────────────────────────┘
- 每个VM有完整OS（几GB）
- 启动慢（分钟级）
- 隔离强

Docker：
┌────────────────────────────────────────────┐
│ App A │ App B │ App C                      │
│ Container │ Container │ Container          │
├────────────────────────────────────────────┤
│            Docker Engine                    │
├────────────────────────────────────────────┤
│            Host OS                          │
├────────────────────────────────────────────┤
│            物理硬件                          │
└────────────────────────────────────────────┘
- 容器共享Host OS内核（MB级）
- 启动快（秒级）
- 隔离较弱（共享内核）
```

**Docker三大概念**：
```
镜像 (Image)    - 只读模板，包含应用和依赖
容器 (Container) - 镜像的运行实例
仓库 (Registry)  - 存储和分发镜像（如Docker Hub）
```

---

### 概念2：Dockerfile基础

```dockerfile
# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 复制依赖文件（先复制这一层，利用缓存）
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码（后复制，因为代码变化频繁）
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["python", "app.py"]
```

**指令说明**：
```
FROM    - 基础镜像（必选）
WORKDIR - 工作目录（不存在会创建）
ENV     - 环境变量
COPY    - 复制文件
RUN     - 构建时执行命令
EXPOSE  - 声明端口（仅文档作用）
CMD     - 容器启动命令
```

---

### 概念3：镜像分层

```
Dockerfile                      镜像层
──────────────────────────────────────────
FROM python:3.11-slim    →     Layer 0 (基础镜像)
WORKDIR /app             →     Layer 1 (目录)
COPY requirements.txt .  →     Layer 2 (依赖文件)
RUN pip install ...      →     Layer 3 (安装依赖)
COPY . .                 →     Layer 4 (代码)
CMD ["python", "app.py"] →     Layer 5 (启动命令)
```

**分层的好处**：
```
第一次构建：下载/创建所有层

修改代码后重建：
- Layer 0-3：缓存命中，跳过
- Layer 4：代码变了，重新构建
- Layer 5：无变化，跳过

结果：只重建变化的层，速度很快！
```

**最佳实践**：
```dockerfile
# 好：先复制不常变化的文件
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# 差：一次复制所有文件
COPY . .
RUN pip install -r requirements.txt
# 代码任何变化都会导致pip重装
```

---

### 概念4：常用命令

```bash
# ========== 镜像操作 ==========
# 构建镜像
docker build -t myapp:v1 .

# 查看镜像
docker images

# 删除镜像
docker rmi myapp:v1

# ========== 容器操作 ==========
# 运行容器
docker run -d -p 8000:8000 --name myapp-container myapp:v1
#   -d: 后台运行
#   -p: 端口映射 (宿主机:容器)
#   --name: 容器名称

# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看日志
docker logs -f myapp-container

# 进入容器
docker exec -it myapp-container bash

# 停止容器
docker stop myapp-container

# 启动已停止的容器
docker start myapp-container

# 删除容器
docker rm myapp-container

# ========== 资源查看 ==========
# 查看容器资源使用
docker stats

# 查看容器详细信息
docker inspect myapp-container
```

---

## 💻 项目代码参考

### 为本项目编写Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8787

# 先复制依赖文件（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8787

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8787/ || exit 1

# 启动命令
CMD ["python", "portal/app.py", "--port", "8787"]
```

**构建和运行**：
```bash
# 构建镜像
docker build -t kl-agent:v1 .

# 运行容器
docker run -d \
    -p 8787:8787 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/config.json:/app/config.json \
    --name kl-agent \
    kl-agent:v1

# 查看日志
docker logs -f kl-agent

# 测试
curl http://localhost:8787/
```

---

## 🔧 动手练习

### 练习10.1：构建第一个镜像

创建一个简单的Python Flask应用并Docker化：

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Docker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

```dockerfile
# Dockerfile
# TODO: 编写Dockerfile
# 要求：
# 1. 使用 python:3.11-slim 基础镜像
# 2. 安装 flask
# 3. 暴露 5000 端口
# 4. 启动 app.py
```

**操作步骤**：
```bash
# 1. 构建镜像
docker build -t my-flask:v1 .

# 2. 运行容器
docker run -d -p 5000:5000 my-flask:v1

# 3. 测试
curl http://localhost:5000

# 4. 查看日志
docker logs <container_id>
```

### 练习10.2：利用镜像缓存

```dockerfile
# 比较：哪种写法构建更快？

# 写法A
COPY . .
RUN pip install flask

# 写法B
COPY requirements.txt .
RUN pip install flask
COPY . .

# 实验：
# 1. 用写法A构建
# 2. 修改 app.py 中的一句话
# 3. 再次构建，观察是否重装了flask
# 4. 改用写法B，重复实验
```

### 练习10.3：容器调试

```bash
# 进入容器内部
docker exec -it <container_id> bash

# 在容器内执行
ls -la /app
cat /etc/os-release
python --version

# 查看容器网络
docker network ls
docker inspect <container_id> | grep IPAddress
```

---

## ✅ 验收标准

1. **问**：Docker容器和虚拟机有什么区别？
   **答**：容器共享宿主机内核，启动快（秒级），体量小（MB）；虚拟机有完整OS，启动慢（分钟），体量大（GB）。

2. **问**：为什么Dockerfile中要先COPY requirements.txt再COPY .？
   **答**：利用镜像分层缓存。依赖文件变化少，代码变化多。这样代码变化时不需要重装依赖。

3. **问**：docker run的-p参数是什么意思？
   **答**：端口映射。`-p 8000:5000` 表示宿主机8000端口映射到容器5000端口。

4. **问**：HEALTHCHECK指令有什么用？
   **答**：定期检查容器健康状态，不健康时可以自动重启。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_11**: Kubernetes基础

---

## 📝 AI Prompt（用于新对话）

```
我正在学习Docker，当前处于阶段10：Docker基础。

我已完成：
- 理解Docker镜像/容器/仓库概念
- 理解Docker与虚拟机的区别
- 掌握Dockerfile基本编写
- 理解镜像分层和缓存原理
- 掌握常用docker命令

请帮我：
1. 检查我的Dockerfile是否写得合理
2. 解释一些Docker概念
3. 给我一个Docker实践练习

我的Dockerfile：
[粘贴你的Dockerfile]

参考项目代码：
- 本项目可Docker化，使用 portal/app.py 作为入口
- 需要暴露 8787 端口
- 需要挂载 data/ 目录和 config.json
```