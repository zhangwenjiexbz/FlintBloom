# FlintBloom

**基于 LangChain 和 LangGraph 的 AI 可观测性平台**

开源的 LangSmith 替代方案，支持本地部署。通过强大的追踪可视化和分析功能，监控、调试和优化你的 LangChain/LangGraph 应用。

[English](README.md) | 简体中文

## ✨ 核心特性

### 🔍 离线分析模式
- **基于 Checkpoint 分析**：直接读取 LangGraph 的 checkpoint 表（CheckpointBlobs、CheckpointWrites、Checkpoints）
- **零运行时开销**：分析历史数据，无需修改应用代码
- **时间旅行调试**：回放和检查任意 checkpoint 状态
- **深度洞察**：提取执行轨迹、Token 使用量和性能指标

### ⚡ 实时追踪模式
- **实时监控**：通过 WebSocket 流式传输执行事件
- **自定义回调**：即插即用的 LangChain 回调处理器
- **事件缓冲**：捕获和回放事件
- **实时指标**：实时追踪 Token 使用和成本

### 🗄️ 多数据库支持
- **MySQL** - 生产级，完整的 JSON 支持
- **PostgreSQL** - 高级 JSONB 查询和索引
- **SQLite** - 轻量级本地开发

### 📊 可视化与分析
- 执行轨迹图
- Token 使用和成本分析
- 性能指标和瓶颈检测
- Checkpoint 对比
- 线程时间线视图

## 🚀 快速开始

### 使用 Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom

# 复制环境配置
cp .env.example .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

API 将在 `http://localhost:8000` 可用

### 手动安装

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境
cp ../.env.example .env
# 编辑 .env 配置数据库

# 运行应用
python -m app.main
```

## 📖 使用方法

### 1. 离线分析模式

分析现有的 LangGraph checkpoint 数据：

```python
import requests

# 列出所有线程
response = requests.get("http://localhost:8000/api/v1/offline/threads")
threads = response.json()

# 获取线程的 checkpoints
thread_id = "your-thread-id"
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/checkpoints")
checkpoints = response.json()

# 获取详细追踪
checkpoint_id = "checkpoint-id"
response = requests.get(
    f"http://localhost:8000/api/v1/offline/threads/{thread_id}/checkpoints/{checkpoint_id}/trace"
)
trace = response.json()

# 分析整个线程
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/analysis")
analysis = response.json()
print(f"总成本: ${analysis['total_cost']:.4f}")
print(f"总 Token: {analysis['total_tokens']}")
```

### 2. 实时追踪模式

在你的 LangChain/LangGraph 应用中添加回调：

```python
from app.modules.realtime.callbacks import FlintBloomCallbackHandler

# 创建回调处理器
callback = FlintBloomCallbackHandler(
    thread_id="my-thread-123",
    enable_streaming=True
)

# 与 LangChain 一起使用
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("解释量子计算")

# 与 LangGraph 一起使用
from langgraph.graph import StateGraph

graph = StateGraph(YourState)
# ... 构建你的图 ...
app = graph.compile()

result = app.invoke(
    {"input": "你的输入"},
    config={"callbacks": [callback]}
)
```

### 3. WebSocket 实时流

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws/my-thread-123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'event') {
        console.log('新事件:', data.data);
        // 更新你的 UI
    }
};

ws.onopen = () => {
    console.log('已连接到 FlintBloom');
};
```

## 🏗️ 架构

```
FlintBloom/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── core/              # 配置与数据库
│   │   ├── db/                # 模型、Schema、适配器
│   │   │   └── adapters/      # MySQL、PostgreSQL、SQLite
│   │   ├── modules/
│   │   │   ├── offline/       # Checkpoint 分析
│   │   │   └── realtime/      # 实时追踪
│   │   └── main.py            # FastAPI 应用
│   └── requirements.txt
├── frontend/                   # React 前端（待完善）
├── docker-compose.yml
└── README.md
```

## 🔧 配置

编辑 `.env` 文件：

```bash
# 数据库类型
DB_TYPE=mysql  # mysql、postgresql 或 sqlite

# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=agentnext

# PostgreSQL 配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=agentnext

# SQLite 配置
SQLITE_PATH=./data/flintbloom.db

# 实时功能
ENABLE_REALTIME=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📚 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

#### 离线分析
- `GET /api/v1/offline/threads` - 列出所有线程
- `GET /api/v1/offline/threads/{thread_id}/checkpoints` - 列出 checkpoints
- `GET /api/v1/offline/threads/{thread_id}/checkpoints/{checkpoint_id}/trace` - 获取追踪
- `GET /api/v1/offline/threads/{thread_id}/analysis` - 分析线程
- `GET /api/v1/offline/threads/{thread_id}/timeline` - 获取时间线

#### 实时追踪
- `WS /api/v1/realtime/ws/{thread_id}` - WebSocket 流
- `GET /api/v1/realtime/threads` - 列出活跃线程
- `GET /api/v1/realtime/threads/{thread_id}/events` - 获取缓冲事件
- `GET /api/v1/realtime/threads/{thread_id}/summary` - 获取摘要

## 🎯 路线图

- [x] 核心后端架构
- [x] 多数据库支持（MySQL、PostgreSQL、SQLite）
- [x] 离线 checkpoint 分析
- [x] 实时追踪与回调
- [x] WebSocket 流式传输
- [ ] React 前端与追踪可视化
- [ ] Checkpoint 回放功能
- [ ] 高级成本优化建议
- [ ] Prompt 版本管理
- [ ] 团队协作功能
- [ ] 导出/导入功能

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

为 LangChain/LangGraph 社区构建的开源 LangSmith 替代方案。

## 📞 支持

- GitHub Issues: [报告问题或请求功能](https://github.com/zhangwenjiexbz/FlintBloom/issues)
- 文档: [完整文档](https://github.com/zhangwenjiexbz/FlintBloom/wiki)

## 🌟 为什么选择 FlintBloom？

### vs LangSmith

| 特性 | FlintBloom | LangSmith |
|------|-----------|-----------|
| 部署方式 | 本地自托管 | 云服务 |
| 数据隐私 | 完全私有 | 数据上传到云端 |
| 成本 | 免费开源 | 按使用量付费 |
| 离线分析 | ✅ 支持 | ❌ 不支持 |
| 实时追踪 | ✅ 支持 | ✅ 支持 |
| 多数据库 | ✅ MySQL/PG/SQLite | ❌ 仅云端 |
| 定制化 | ✅ 完全可定制 | ❌ 受限 |

### 适用场景

✅ **适合使用 FlintBloom：**
- 需要数据隐私和本地部署
- 已有 LangGraph checkpoint 数据需要分析
- 希望零成本使用可观测性工具
- 需要定制化功能
- 离线环境或内网部署

❌ **可能更适合 LangSmith：**
- 不想自己维护基础设施
- 需要企业级支持
- 团队分布在不同地理位置

## 💡 使用技巧

### 1. 连接现有数据库

如果你已经有 LangGraph checkpoint 数据：

```bash
# 编辑 .env 文件
DB_TYPE=mysql
MYSQL_HOST=your-existing-host
MYSQL_DATABASE=your-existing-database

# 重启服务
docker-compose restart backend
```

### 2. 成本分析

```python
# 获取线程的成本分析
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/analysis")
analysis = response.json()

print(f"总成本: ${analysis['total_cost']:.4f}")
print(f"平均每个 checkpoint 成本: ${analysis['avg_cost_per_checkpoint']:.4f}")
print(f"总 Token: {analysis['total_tokens']}")
```

### 3. 性能优化

```python
# 获取性能指标
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/checkpoints/{checkpoint_id}/trace")
trace = response.json()

summary = trace['summary']
perf = summary['performance_metrics']

print(f"总耗时: {perf['total_duration_ms']:.2f}ms")
print(f"LLM 耗时: {perf['llm_duration_ms']:.2f}ms")
print(f"工具耗时: {perf['tool_duration_ms']:.2f}ms")
```

## 🔥 快速命令

```bash
# 启动服务
make quickstart

# 查看日志
make docker-logs

# 运行测试
make test

# 格式化代码
make format

# 停止服务
make docker-down
```

---

**FlintBloom** - 让 AI 开发透明可调试 🌸
