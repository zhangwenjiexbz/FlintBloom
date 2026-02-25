# FlintBloom 快速参考

## 📦 安装

```bash
# 仅客户端（推荐用于应用集成）
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# 完整服务器
pip install "git+https://github.com/zhangwenjiexbz/FlintBloom.git#egg=flintbloom[server]"

# 开发模式
cd /path/to/FlintBloom
pip install -e .
```

## 🚀 基础使用

### 导入

```python
from flintbloom import FlintBloomCallbackHandler
```

### 创建回调

```python
# 方式 1: 自动检测 thread_id（推荐）
callback = FlintBloomCallbackHandler()

# 方式 2: 自定义解析器
callback = FlintBloomCallbackHandler(
    thread_id_resolver=lambda m: f"user-{m.get('user_id')}"
)

# 方式 3: 静态 thread_id
callback = FlintBloomCallbackHandler(thread_id="my-thread")
```

### 使用回调

```python
# LangChain
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Hello")

# LangGraph
app.invoke(
    input_data,
    config={
        "configurable": {"thread_id": "user-123"},
        "callbacks": [callback]
    }
)
```

## 🎯 常见场景

### 场景 1: FastAPI + LangGraph

```python
from fastapi import FastAPI
from flintbloom import FlintBloomCallbackHandler

app = FastAPI()
callback = FlintBloomCallbackHandler()

@app.post("/chat")
async def chat(user_id: str, message: str):
    thread_id = f"user-{user_id}"
    result = agent.invoke(
        {"messages": [message]},
        config={
            "configurable": {"thread_id": thread_id},
            "callbacks": [callback]
        }
    )
    return {"response": result, "thread_id": thread_id}
```

### 场景 2: 多租户应用

```python
def tenant_resolver(metadata):
    return f"tenant/{metadata['tenant_id']}/user/{metadata['user_id']}"

callback = FlintBloomCallbackHandler(thread_id_resolver=tenant_resolver)

# 使用
llm.invoke(
    "Hello",
    config={"metadata": {"tenant_id": "company-a", "user_id": "user-1"}}
)
```

### 场景 3: 批量处理

```python
callback = FlintBloomCallbackHandler(
    thread_id_resolver=lambda m: f"batch-{m.get('batch_id')}-item-{m.get('item_id')}"
)

for item in items:
    llm.invoke(
        item.text,
        config={"metadata": {"batch_id": "batch-001", "item_id": item.id}}
    )
```

## 🔍 查看追踪

### API 端点

```bash
# 列出线程
curl http://localhost:8000/api/v1/realtime/threads

# 查看事件
curl http://localhost:8000/api/v1/realtime/threads/{thread_id}/events

# 获取摘要
curl http://localhost:8000/api/v1/realtime/threads/{thread_id}/summary
```

### Python 客户端

```python
import requests

# 获取事件
response = requests.get(
    f"http://localhost:8000/api/v1/realtime/threads/{thread_id}/events"
)
events = response.json()

# 获取摘要
response = requests.get(
    f"http://localhost:8000/api/v1/realtime/threads/{thread_id}/summary"
)
summary = response.json()
print(f"Total tokens: {summary['total_tokens']}")
```

## ⚙️ 配置选项

### FlintBloomCallbackHandler 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `thread_id` | `str` | `None` | 静态 thread_id |
| `api_url` | `str` | `http://localhost:8000/api/v1/realtime` | API 地址 |
| `enable_streaming` | `bool` | `True` | 是否启用实时流 |
| `thread_id_resolver` | `callable` | `None` | 自定义解析函数 |
| `auto_detect_thread_id` | `bool` | `True` | 自动检测 thread_id |

### 示例

```python
callback = FlintBloomCallbackHandler(
    thread_id="fallback-thread",  # 后备 thread_id
    api_url="http://flintbloom.example.com/api/v1/realtime",
    enable_streaming=True,
    thread_id_resolver=my_resolver,
    auto_detect_thread_id=True
)
```

## 🎨 Thread ID 命名规范

### 推荐格式

```
{层级1}/{层级2}/{层级3}
```

### 示例

```python
# 用户会话
"user-{user_id}-session-{session_id}"
# 结果: user-123-session-abc

# 多租户
"tenant/{tenant_id}/user/{user_id}/conv/{conv_id}"
# 结果: tenant/company-a/user/alice/conv/conv-001

# 项目环境
"{project}/{env}/{user}"
# 结果: my-app/prod/user-789

# 批处理
"batch/{batch_id}/item/{item_id}"
# 结果: batch/batch-001/item/item-123
```

## 🔄 Thread ID 解析优先级

1. **自定义解析器** (`thread_id_resolver`)
2. **LangGraph config** (`config.configurable.thread_id`)
3. **Metadata** (`metadata.thread_id`)
4. **静态 thread_id** (构造函数参数)
5. **自动生成** (基于 run_id)

## 🐛 故障排查

### 问题 1: 无法导入 FlintBloomCallbackHandler

```bash
# 解决方案：确保已安装
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# 验证安装
python -c "from flintbloom import FlintBloomCallbackHandler; print('OK')"
```

### 问题 2: Thread ID 没有正确检测

```python
# 调试：添加日志
def debug_resolver(metadata):
    thread_id = metadata.get("user_id", "default")
    print(f"Resolved thread_id: {thread_id} from {metadata}")
    return thread_id

callback = FlintBloomCallbackHandler(thread_id_resolver=debug_resolver)
```

### 问题 3: 事件没有发送到服务器

```python
# 检查 API 地址
callback = FlintBloomCallbackHandler(
    api_url="http://localhost:8000/api/v1/realtime",  # 确保正确
    enable_streaming=True  # 确保启用
)

# 测试连接
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())  # 应该返回 {"status": "healthy"}
```

## 📚 更多资源

- **完整文档**: [README.md](README.md)
- **安装指南**: [INSTALL.md](INSTALL.md)
- **集成指南**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **示例代码**: [example_dynamic_threadid.py](backend/example_dynamic_threadid.py)

## 💡 最佳实践

1. **使用自动检测** - 让 FlintBloom 从 LangGraph config 自动提取 thread_id
2. **层级命名** - 使用 `/` 分隔的层级结构便于组织和查询
3. **错误处理** - 在自定义解析器中添加 try-except
4. **性能考虑** - 事件发送是异步的，不会阻塞主流程
5. **安全性** - 不要在 thread_id 中包含敏感信息

## 🎯 快速测试

```python
# test_flintbloom.py
from flintbloom import FlintBloomCallbackHandler
from langchain_openai import ChatOpenAI

# 创建回调
callback = FlintBloomCallbackHandler()

# 测试
llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Say hello")

print("✅ FlintBloom 工作正常！")
print(f"查看追踪: http://localhost:8000/api/v1/realtime/threads")
```

---

**FlintBloom** - 让 AI 开发透明可调试 🌸
