# FlintBloom 安装和集成指南

## 问题 1: 在其他项目中使用 FlintBloom

### 方案 A: 作为 Python 包安装（推荐）

#### 1. 从源码安装

```bash
# 在你的项目中
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# 或者本地安装（开发模式）
cd /path/to/FlintBloom
pip install -e .
```

#### 2. 使用

```python
# 现在可以直接导入
from flintbloom import FlintBloomCallbackHandler

# 使用回调
callback = FlintBloomCallbackHandler()
```

### 方案 B: 复制轻量级客户端

如果不想安装整个包，只需复制客户端文件：

```bash
# 复制到你的项目
cp /path/to/FlintBloom/backend/flintbloom/callbacks.py your_project/flintbloom_client.py
```

```python
# 使用
from your_project.flintbloom_client import FlintBloomCallbackHandler
```

---

## 问题 2: 动态 Thread ID

新版本的 `FlintBloomCallbackHandler` 支持多种方式获取 thread_id：

### 方式 1: 自动检测（推荐 - LangGraph）

```python
from flintbloom import FlintBloomCallbackHandler

# 创建回调，不指定 thread_id
callback = FlintBloomCallbackHandler(
    api_url="http://localhost:8000/api/v1/realtime"
)

# LangGraph 会自动从 config 中提取 thread_id
app.invoke(
    input_data,
    config={
        "configurable": {"thread_id": "user-123-session-456"},  # 自动检测
        "callbacks": [callback]
    }
)
```

### 方式 2: 自定义解析器

```python
from flintbloom import FlintBloomCallbackHandler

# 定义自定义解析函数
def resolve_thread_id(metadata):
    """从 metadata 中提取 thread_id"""
    # 可以根据用户 ID、会话 ID 等生成
    user_id = metadata.get("user_id", "anonymous")
    session_id = metadata.get("session_id", "default")
    return f"{user_id}-{session_id}"

# 使用自定义解析器
callback = FlintBloomCallbackHandler(
    thread_id_resolver=resolve_thread_id
)

# 在调用时传入 metadata
llm.invoke(
    "Hello",
    config={
        "metadata": {
            "user_id": "user-123",
            "session_id": "session-456"
        },
        "callbacks": [callback]
    }
)
```

### 方式 3: 静态 Thread ID（简单场景）

```python
# 仍然支持静态 thread_id
callback = FlintBloomCallbackHandler(thread_id="my-static-thread")
```

### 方式 4: 从请求上下文动态获取

```python
from contextvars import ContextVar
from flintbloom import FlintBloomCallbackHandler

# 使用 context variable 存储当前请求的 thread_id
current_thread_id = ContextVar('thread_id', default='default')

def get_thread_id_from_context(metadata):
    """从上下文中获取 thread_id"""
    return current_thread_id.get()

callback = FlintBloomCallbackHandler(
    thread_id_resolver=get_thread_id_from_context
)

# 在 API 请求处理中设置
@app.post("/chat")
async def chat(request: ChatRequest):
    # 根据用户生成 thread_id
    thread_id = f"user-{request.user_id}-{request.session_id}"
    current_thread_id.set(thread_id)

    # 使用回调
    result = await agent.ainvoke(
        request.message,
        config={"callbacks": [callback]}
    )
    return result
```

---

## 完整示例

### 示例 1: FastAPI + LangGraph + 动态 Thread ID

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flintbloom import FlintBloomCallbackHandler
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

app = FastAPI()

# 创建 LangGraph 应用
def create_agent():
    workflow = StateGraph(AgentState)
    # ... 构建你的图
    checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
    return workflow.compile(checkpointer=checkpointer)

agent = create_agent()

# 创建回调（自动检测 thread_id）
callback = FlintBloomCallbackHandler(
    api_url="http://localhost:8000/api/v1/realtime",
    auto_detect_thread_id=True
)

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # 动态生成 thread_id
    thread_id = f"user-{request.user_id}-session-{request.session_id}"

    # LangGraph 配置
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [callback]
    }

    # 执行
    result = agent.invoke(
        {"messages": [request.message]},
        config=config
    )

    return {
        "response": result,
        "thread_id": thread_id,
        "trace_url": f"http://localhost:8000/api/v1/realtime/threads/{thread_id}/events"
    }
```

### 示例 2: 多租户场景

```python
from flintbloom import FlintBloomCallbackHandler

def get_tenant_thread_id(metadata):
    """为多租户生成隔离的 thread_id"""
    tenant_id = metadata.get("tenant_id", "default")
    user_id = metadata.get("user_id", "anonymous")
    conversation_id = metadata.get("conversation_id", "new")

    # 格式: tenant-{tenant_id}/user-{user_id}/conv-{conversation_id}
    return f"tenant-{tenant_id}/user-{user_id}/conv-{conversation_id}"

# 创建回调
callback = FlintBloomCallbackHandler(
    thread_id_resolver=get_tenant_thread_id,
    api_url="http://localhost:8000/api/v1/realtime"
)

# 使用
result = llm.invoke(
    "Hello",
    config={
        "metadata": {
            "tenant_id": "company-abc",
            "user_id": "user-123",
            "conversation_id": "conv-456"
        },
        "callbacks": [callback]
    }
)

# Thread ID 将是: tenant-company-abc/user-user-123/conv-conv-456
```

### 示例 3: 基于时间的 Thread ID

```python
from datetime import datetime
from flintbloom import FlintBloomCallbackHandler

def time_based_thread_id(metadata):
    """基于时间和用户生成 thread_id"""
    user_id = metadata.get("user_id", "anonymous")
    timestamp = datetime.now().strftime("%Y%m%d-%H")
    return f"{user_id}-{timestamp}"

callback = FlintBloomCallbackHandler(
    thread_id_resolver=time_based_thread_id
)

# 每小时会生成新的 thread_id，便于按时间段分析
```

---

## Thread ID 解析优先级

`FlintBloomCallbackHandler` 按以下优先级解析 thread_id：

1. **自定义解析器** (`thread_id_resolver`)
2. **LangGraph config** (`config.configurable.thread_id`)
3. **Metadata** (`metadata.thread_id`)
4. **静态 thread_id** (构造函数参数)
5. **自动生成** (基于 run_id)

---

## 最佳实践

### 1. 生产环境推荐

```python
# 使用自定义解析器 + 自动检测
callback = FlintBloomCallbackHandler(
    thread_id_resolver=your_custom_resolver,
    auto_detect_thread_id=True,
    api_url=os.getenv("FLINTBLOOM_API_URL", "http://localhost:8000/api/v1/realtime")
)
```

### 2. Thread ID 命名规范

建议使用层级结构：

```
{tenant}/{user}/{session}
{project}/{environment}/{user}
{service}/{version}/{request_id}
```

示例：
- `company-abc/user-123/session-456`
- `my-app/prod/user-789`
- `chatbot/v2/req-abc123`

### 3. 错误处理

```python
def safe_thread_id_resolver(metadata):
    """带错误处理的解析器"""
    try:
        user_id = metadata.get("user_id")
        if not user_id:
            return "anonymous"
        return f"user-{user_id}"
    except Exception as e:
        print(f"Error resolving thread_id: {e}")
        return "error-fallback"

callback = FlintBloomCallbackHandler(
    thread_id_resolver=safe_thread_id_resolver
)
```

---

## 迁移指南

### 从旧版本迁移

**旧代码：**
```python
callback = FlintBloomCallbackHandler(thread_id="static-thread")
```

**新代码（推荐）：**
```python
# 方式 1: 自动检测
callback = FlintBloomCallbackHandler()

# 方式 2: 自定义解析
callback = FlintBloomCallbackHandler(
    thread_id_resolver=lambda m: m.get("user_id", "default")
)
```

---

## 常见问题

### Q1: 如何在不同的请求中使用不同的 thread_id？

A: 使用自动检测或自定义解析器，在每次调用时通过 config 传入不同的标识。

### Q2: 可以在运行时更改 thread_id 吗？

A: 可以。每次调用时，回调会重新解析 thread_id。

### Q3: 如何调试 thread_id 解析？

A: 可以在解析器中添加日志：

```python
def debug_resolver(metadata):
    thread_id = metadata.get("user_id", "default")
    print(f"Resolved thread_id: {thread_id} from metadata: {metadata}")
    return thread_id
```

### Q4: 性能影响如何？

A: thread_id 解析非常轻量，几乎没有性能影响。事件发送是异步的，不会阻塞主流程。

---

## 总结

✅ **问题 1 已解决**: 通过 pip 安装或复制客户端文件即可在其他项目中使用

✅ **问题 2 已解决**: 支持多种动态 thread_id 获取方式，包括：
- 自动从 LangGraph config 检测
- 自定义解析函数
- 从上下文变量获取
- 静态配置（向后兼容）

推荐使用自动检测 + 自定义解析器的组合，既灵活又强大！
