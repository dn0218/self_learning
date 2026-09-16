# 学习阶段 05：Linux进程与系统监控

## 📌 阶段信息
- **阶段编号**: 05
- **前置要求**: 完成STAGE_01-04
- **预计时间**: 3-4天
- **目标岗位**: SRE / DevOps / Linux系统管理员

---

## 🎯 学习目标

1. 理解Linux进程的状态和生命周期
2. 掌握top/vmstat/iostat的使用和含义
3. 理解load average的含义
4. 掌握基础的系统排查思路

---

## 📚 核心概念

### 概念1：进程状态

Linux进程有5种基本状态：

```
R (Running)      - 正在运行或等待CPU
S (Sleeping)     - 可中断睡眠，等待事件（最常见）
D (Disk Sleep)   - 不可中断睡眠，通常在等待IO
Z (Zombie)       - 僵尸进程，已结束但父进程未回收
T (Stopped)      - 被暂停（如Ctrl+Z）
```

**查看进程状态**：
```bash
# 使用ps命令
ps aux

# 输出解释
USER    PID  %CPU %MEM  VSZ   RSS   TTY  STAT START  TIME  COMMAND
root    1    0.0  0.1   1234  567   ?    Ss   10:00  0:01  /sbin/init
#                       STAT列：S=Sleeping, s=会话领导者

# 查看特定进程
ps aux | grep nginx
```

**僵尸进程问题**：
```bash
# 查找僵尸进程
ps aux | awk '$8 ~ /Z/ {print}'

# 僵尸进程不能直接kill，需要：
# 1. 重启父进程
# 2. 或修改父进程代码正确回收子进程
```

---

### 概念2：Load Average

```bash
$ uptime
 14:30:22 up 10 days,  3 users,  load average: 0.52, 0.58, 0.59
#                                         过去1分钟 5分钟 15分钟
```

**Load Average是什么？**
- 运行队列长度 = 正在运行的进程数 + 等待CPU的进程数
- 不只是CPU使用率，还包括等待IO的进程

**如何判断是否过载？**
```
单核CPU：load 1.0 = 100%利用率
4核CPU：load 4.0 = 100%利用率
8核CPU：load 8.0 = 100%利用率

一般规则：
- load < 核心数：正常
- load ≈ 核心数：接近满载
- load > 核心数：过载，需要关注
```

**查看CPU核心数**：
```bash
# 方法1
nproc

# 方法2
cat /proc/cpuinfo | grep "processor" | wc -l

# 方法3
lscpu
```

---

### 概念3：top命令详解

```bash
$ top
top - 14:30:22 up 10 days,  3 users,  load average: 0.52, 0.58, 0.59
Tasks: 150 total,   1 running, 149 sleeping,   0 stopped,   0 zombie
%Cpu(s):  5.9 us,  2.1 sy,  0.0 ni, 91.5 id,  0.5 wa,  0.0 hi,  0.0 si
MiB Mem :   7823.5 total,    256.3 free,   2100.2 used,   5467.0 buff/cache
```

**CPU行详解**：
```
us (user)    - 用户态程序占用（应用代码）
sy (system)  - 内核态占用（系统调用）
id (idle)    - 空闲
wa (I/O wait) - 等待IO（磁盘/网络）

分析：
- us高：CPU密集型应用，考虑优化代码
- sy高：大量系统调用，检查是否有频繁的IO操作
- wa高：IO瓶颈，检查磁盘或网络
- id低但us/sy/wa都不高：可能在等待其他资源
```

**内存行详解**：
```
total       - 总内存
free        - 完全空闲
used        - 已使用（不含buff/cache）
buff/cache  - 内核用于缓存的内存（可回收）

关键：available ≈ free + 可回收的buff/cache
实际可用内存看available，不是free！
```

**交互操作**：
```bash
# 在top运行时按这些键
P - 按CPU使用率排序（默认）
M - 按内存使用率排序
T - 按运行时间排序
k - kill进程（输入PID）
q - 退出
1 - 显示每个CPU核心
```

---

### 概念4：vmstat详解

```bash
$ vmstat 1  # 每秒刷新
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs  us sy id wa st
 1  0      0 256300 102400 5467000    0    0     0    10  100  200   5  2 92  0  0
```

**各列含义**：
```
procs:
  r - 运行队列长度（等待CPU的进程数）
  b - 不可中断睡眠的进程数（等待IO）

memory:
  swpd - 已使用的交换区
  free - 空闲内存
  buff - 缓冲区
  cache - 页缓存

swap:
  si - 从交换区读入（swap in）/秒
  so - 写入交换区（swap out）/秒
  → si/so不为0说明内存不足，在用交换区！

io:
  bi - 从块设备读入/秒
  bo - 写入块设备/秒

cpu:
  us/sy/id/wa - 与top相同
```

**排查思路**：
```
r列持续高 → CPU过载，需要扩容或优化
b列持续高 → IO瓶颈，检查磁盘
si/so高 → 内存不足，增加内存或优化程序
wa高 → IO等待，检查磁盘性能
```

---

### 概念5：iostat详解

```bash
$ iostat -x 1  # 详细模式，每秒刷新
Device         r/s     w/s     rMB/s   wMB/s   %util   await
sda           10.0    5.0     0.1     0.05    5.0     2.0
```

**关键指标**：
```
r/s, w/s   - 每秒读/写次数（IOPS）
rMB/s, wMB/s - 每秒读/写吞吐量
%util      - 设备利用率（接近100%说明磁盘饱和）
await      - 平均IO等待时间（毫秒）
           → 超过10ms通常认为有问题
```

---

## 💻 项目代码参考

### 来源：pipeline.py - 健康检查超时

```python
PROBE_TIMEOUT = 20  # 健康检查超时时间

def probe_site(url: str):
    try:
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as r:
            # ...
    except Exception as e:
        # 超时或连接失败
```

**理解**：
- 所有网络操作都必须有超时设置
- 20秒是一个合理的默认值
- 超时保护防止进程卡死

---

### 来源：portal/app.py - 后台线程

```python
def run_pipeline_background(slug):
    def _run():
        subprocess.run([sys.executable, "pipeline.py", "--rebuild", slug])
    
    threading.Thread(target=_run, daemon=True).start()
```

**进程视角理解**：
- `daemon=True` 表示守护线程
- 主进程退出时，守护线程自动终止
- 用`ps aux | grep python`可以看到这些线程

---

## 🔧 动手练习

### 练习5.1：分析系统状态

在Linux环境（或WSL）中执行：

```bash
# 1. 查看系统负载
uptime

# 2. 查看CPU核心数
nproc

# 3. 判断：当前系统是否过载？

# 4. 使用top找出占用CPU最多的进程
top -c

# 5. 使用vmstat分析系统瓶颈
vmstat 1 5
```

### 练习5.2：内存分析

```bash
# 1. 查看内存状态
free -h

# 2. 理解buff/cache
cat /proc/meminfo | head -20

# 3. 问题：为什么free很少但系统正常？
# 答案：Linux会主动把空闲内存用于缓存，看available才是实际可用
```

### 练习5.3：排查模拟

**场景**：一个Web服务响应很慢

```bash
# 步骤1：查看负载
uptime
# 如果load很高，继续排查

# 步骤2：查看CPU使用
top
# 如果us高：应用代码消耗大
# 如果wa高：IO瓶颈

# 步骤3：查看内存
free -h
vmstat 1
# 如果si/so高：内存不足，在用交换区

# 步骤4：查看磁盘
iostat -x 1
# 如果%util高：磁盘瓶颈
# 如果await高：IO延迟大
```

---

## ✅ 验收标准

1. **问**：load average 2.5 在2核CPU上意味着什么？
   **答**：过载。2核满载是load 2.0，2.5表示有进程在等待CPU。

2. **问**：free内存很少但系统正常，为什么？
   **答**：Linux会主动用空闲内存做缓存（buff/cache），看available才是实际可用。

3. **问**：vmstat中si/so不为0说明什么？
   **答**：内存不足，系统在使用交换区（swap）。这是性能警告信号。

4. **问**：iostat中await超过10ms意味着什么？
   **答**：IO延迟较高，磁盘可能是性能瓶颈。

---

## 🔗 下一步

完成本阶段后，进入：
- **STAGE_06**: Linux网络与端口

---

## 📝 AI Prompt（用于新对话）

```
我正在学习SRE/DevOps技术栈，当前处于阶段05：Linux进程与系统监控。

我已完成：
- 理解进程5种状态（R/S/D/Z/T）
- 理解load average的含义（运行队列长度）
- 掌握top/vmstat/iostat的基本使用
- 掌握基础排查思路（CPU/内存/IO）

请帮我：
1. 确认我对系统监控概念的理解是否正确
2. 给我一个模拟故障场景，让我分析原因

我的系统信息：
[粘贴 uptime, nproc, free -h 的输出]

参考项目代码：
- pipeline.py 使用 timeout=20 进行超时保护
- portal/app.py 使用 daemon=True 创建守护线程
```