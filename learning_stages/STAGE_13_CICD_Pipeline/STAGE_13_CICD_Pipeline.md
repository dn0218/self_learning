# 学习阶段 13：CI/CD Pipeline基础

## 📌 阶段信息
- **阶段编号**: 13
- **前置要求**: 完成STAGE_10（Docker）
- **预计时间**: 2-3天
- **目标岗位**: SRE / DevOps

---

## 🎯 学习目标

1. 理解CI/CD的核心概念
2. 掌握GitHub Actions基本配置
3. 理解Pipeline的典型阶段
4. 能够为learning_stages创建自动部署流程

---

## 📚 核心概念

### 概念1：什么是CI/CD？

```
CI (Continuous Integration) - 持续集成
┌─────────────────────────────────────────────────┐
│  开发者提交代码 → 自动构建 → 自动测试 → 反馈结果 │
│                                                 │
│  目的：尽早发现问题，避免集成地狱                │
└─────────────────────────────────────────────────┘

CD (Continuous Deployment/Delivery) - 持续部署
┌─────────────────────────────────────────────────┐
│  测试通过 → 自动部署到测试环境 → 自动部署到生产  │
│                                                 │
│  目的：快速、安全、可重复的发布流程               │
└─────────────────────────────────────────────────┘
```

**完整流程**：
```
代码提交 → 构建 → 测试 → 打包 → 部署测试环境 → 部署生产环境
    │        │      │      │         │              │
    └────────┴──────┴──────┴─────────┴──────────────┘
                      CI              CD
```

---

### 概念2：GitHub Actions基础

**基本结构**：
```yaml
# .github/workflows/main.yml
name: CI Pipeline                    # 工作流名称

on:                                  # 触发条件
  push:                              # 推送时触发
    branches: [main]                 # 仅main分支
  pull_request:                      # PR时触发
    branches: [main]

jobs:                                # 任务列表
  build:                             # 任务名称
    runs-on: ubuntu-latest           # 运行环境
    
    steps:                           # 步骤列表
    - name: Checkout code            # 步骤名称
      uses: actions/checkout@v4      # 使用预定义action
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run tests
      run: pytest
```

---

### 概念3：Pipeline典型阶段

```
┌──────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Stage 1: 代码检查                                            │
│  ├── Lint (代码风格检查)                                       │
│  └── Security Scan (安全扫描)                                  │
│                                                               │
│  Stage 2: 构建                                                │
│  ├── Compile (编译)                                           │
│  └── Build Image (构建Docker镜像)                              │
│                                                               │
│  Stage 3: 测试                                                │
│  ├── Unit Tests (单元测试)                                     │
│  ├── Integration Tests (集成测试)                              │
│  └── E2E Tests (端到端测试)                                    │
│                                                               │
│  Stage 4: 部署                                                │
│  ├── Deploy to Staging (部署到测试环境)                        │
│  ├── Smoke Tests (冒烟测试)                                    │
│  └── Deploy to Production (部署到生产环境)                     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

### 概念4：环境管理

```
Development (开发环境)
    │ 开发者本地或云端开发环境
    │ 用于日常开发和调试
    ▼
Staging (预发布环境)
    │ 类似生产环境的测试环境
    │ 用于最终测试和验证
    ▼
Production (生产环境)
    │ 面向用户的正式环境
    │ 需要严格的发布流程
```

**最佳实践**：
- 生产环境部署需要手动批准
- 使用相同的Docker镜像跨环境
- 配置通过环境变量注入

---

## 💻 为learning_stages创建CI配置

### 简单的文档检查Pipeline

```yaml
# .github/workflows/docs-check.yml
name: Documentation Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Check Markdown files exist
      run: |
        echo "检查学习阶段文件..."
        for i in $(seq -w 1 12); do
          if [ -f "learning_stages/STAGE_${i}_*/STAGE_${i}_*.md" ]; then
            echo "✓ STAGE_${i} 文件存在"
          else
            echo "✗ STAGE_${i} 文件缺失"
            exit 1
          fi
        done
    
    - name: Check INSTRUCTOR files
      run: |
        echo "检查指导员文件..."
        find learning_stages -name "INSTRUCTOR.md" | wc -l
```

### 部署到GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup Pages
      uses: actions/configure-pages@v4
    
    - name: Build
      run: |
        # 创建简单的HTML索引页
        cat > index.html << 'EOF'
        <!DOCTYPE html>
        <html>
        <head>
          <title>SRE/DevOps Learning Path</title>
        </head>
        <body>
          <h1>SRE/DevOps 学习路径</h1>
          <ul>
            <li><a href="learning_stages/README.md">总览</a></li>
            <li><a href="learning_stages/STAGE_01_HTTP_Basics/">Stage 01: HTTP基础</a></li>
            <!-- 更多阶段 -->
          </ul>
        </body>
        </html>
        EOF
    
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: '.'
    
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

---

## 🔧 动手练习

### 练习13.1：创建GitHub仓库并推送

```bash
# 1. 在GitHub创建新仓库（浏览器操作）
# 仓库名：self_learning

# 2. 本地初始化
cd /path/to/your/project
git init
git add .
git commit -m "Initial commit: learning stages"

# 3. 关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/self_learning.git
git branch -M main
git push -u origin main
```

### 练习13.2：添加GitHub Actions

```bash
# 创建workflow目录
mkdir -p .github/workflows

# 创建简单的CI配置
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: List files
      run: ls -la learning_stages/
    - name: Check README
      run: test -f learning_stages/README.md && echo "README exists"
EOF

# 提交并推送
git add .github/
git commit -m "Add CI workflow"
git push
```

### 练习13.3：查看CI运行结果

```
1. 打开GitHub仓库页面
2. 点击 "Actions" 标签
3. 查看工作流运行状态
4. 点击具体的运行查看详细日志
```

---

## ✅ 验收标准

1. **问**：CI和CD分别是什么？
   **答**：CI是持续集成（自动构建测试），CD是持续部署（自动发布）。

2. **问**：GitHub Actions的on字段定义什么？
   **答**：触发条件，如何时运行工作流（push、pull_request等）。

3. **问**：为什么要区分测试环境和生产环境？
   **答**：测试环境验证不影响用户，生产环境需严格流程保护。

4. **问**：为什么生产部署需要手动批准？
   **答**：避免自动化意外发布，人工确认确保质量。

---

## 🔗 学习总结

恭喜完成全部13个阶段！现在你可以：

1. 将learning_stages推送到GitHub
2. 在任何设备上克隆继续学习
3. 使用GitHub Actions自动化文档检查

---

## 📝 AI Prompt（用于新对话）

```
我正在学习CI/CD，当前处于阶段13：CI/CD Pipeline基础。

我已完成：
- 理解CI/CD概念（持续集成、持续部署）
- 掌握GitHub Actions基本配置
- 理解Pipeline的典型阶段
- 能够创建简单的自动化流程

请帮我：
1. 检查我的GitHub Actions配置是否正确
2. 解释CI/CD相关概念
3. 给我一个更复杂的Pipeline练习

我的配置文件：
[粘贴你的workflow配置]
```