# FlintBloom 安装指南

## 📦 安装方式

FlintBloom 提供三种安装方式，根据你的需求选择：

### 方式 1: 仅安装客户端（推荐用于应用集成）

如果你只需要在自己的应用中使用 FlintBloom 的回调功能，安装轻量级客户端即可：

```bash
# 从 GitHub 安装
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# 或从本地安装（开发模式）
cd /path/to/FlintBloom
pip install -e .
```

**依赖项**：仅需要 `langchain-core` 和 `requests`，非常轻量！

**使用**：
```python
from flintbloom import FlintBloomCallbackHandler

callback = FlintBloomCallbackHandler()
# 使用回调...
```

### 方式 2: 安装完整服务器

如果你需要运行 FlintBloom 服务器（API + 数据库）：

```bash
# 安装服务器版本
pip install "git+https://github.com/zhangwenjiexbz/FlintBloom.git#egg=flintbloom[server]"

# 或本地安装
cd /path/to/FlintBloom
pip install -e ".[server]"
```

**包含**：FastAPI、数据库驱动、完整的后端功能

### 方式 3: 开发者安装（包含测试工具）

如果你要参与 FlintBloom 开发：

```bash
cd /path/to/FlintBloom
pip install -e ".[all]"
```

**包含**：服务器 + 开发工具（pytest、black、mypy 等）

---

## 🚀 快速开始

### 场景 1: 在现有项目中使用（仅客户端）

```bash
# 1. 安装客户端
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# 2. 在代码中使用
```

```python
from flintbloom import FlintBloomCallbackHandler
from langchain_openai import ChatOpenAI

# 创建回调（自动检测 thread_id）
callback = FlintBloomCallbackHandler(
    api_url="http://your-flintbloom-server:8000/api/v1/realtime"
)

# 使用
llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Hello")
```

### 场景 2: 部署完整的 FlintBloom 服务

```bash
# 1. 克隆仓库
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom

# 2. 使用 Docker Compose（推荐）
docker-compose up -d

# 或手动安装
pip install -e ".[server]"
cp .env.example .env
# 编辑 .env 配置数据库
python -m app.main
```

### 场景 3: 开发和贡献

```bash
# 1. Fork 并克隆
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom

# 2. 安装开发依赖
pip install -e ".[all]"

# 3. 运行测试
pytest

# 4. 格式化代码
black backend/
isort backend/
```

---

## 📋 依赖说明

### 客户端依赖（最小化）

```
langchain-core>=1.0.0
requests>=2.31.0
```

### 服务器额外依赖

```
fastapi>=0.115.0
uvicorn>=0.32.0
sqlalchemy>=2.0.35
langchain>=1.0.0
langgraph>=1.0.0
# ... 更多
```

### 开发工具依赖

```
pytest>=7.4.3
black>=23.12.1
mypy>=1.7.1
# ... 更多
```

---

## 🔧 配置

### 客户端配置

客户端只需要知道 FlintBloom 服务器的地址：

```python
callback = FlintBloomCallbackHandler(
    api_url="http://localhost:8000/api/v1/realtime",  # 服务器地址
    enable_streaming=True  # 是否启用实时流
)
```

### 服务器配置

编辑 `.env` 文件：

```bash
# 数据库类型
DB_TYPE=mysql  # mysql, postgresql, 或 sqlite

# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=agentnext

# 其他配置...
```

---

## 📦 在 requirements.txt 中使用

### 仅客户端

```txt
# requirements.txt
flintbloom @ git+https://github.com/zhangwenjiexbz/FlintBloom.git
```

### 包含服务器

```txt
# requirements.txt
flintbloom[server] @ git+https://github.com/zhangwenjiexbz/FlintBloom.git
```

### 指定版本

```txt
# requirements.txt
flintbloom @ git+https://github.com/zhangwenjiexbz/FlintBloom.git@v0.1.0
```

---

## 🐳 Docker 安装

### 使用预构建镜像（未来）

```bash
docker pull flintbloom/flintbloom:latest
docker run -p 8000:8000 flintbloom/flintbloom:latest
```

### 使用 Docker Compose

```bash
# 克隆仓库
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

---

## 🔍 验证安装

### 验证客户端安装

```python
# test_install.py
try:
    from flintbloom import FlintBloomCallbackHandler
    print("✅ FlintBloom 客户端安装成功！")
    print(f"   版本: {FlintBloomCallbackHandler.__module__}")
except ImportError as e:
    print(f"❌ 安装失败: {e}")
```

### 验证服务器安装

```bash
# 检查 API 是否运行
curl http://localhost:8000/health

# 应该返回
# {"status":"healthy","version":"0.1.0","database":"mysql"}
```

---

## 🆙 升级

### 升级客户端

```bash
pip install --upgrade git+https://github.com/zhangwenjiexbz/FlintBloom.git
```

### 升级服务器

```bash
cd /path/to/FlintBloom
git pull
pip install --upgrade -e ".[server]"

# 如果使用 Docker
docker-compose pull
docker-compose up -d
```

---

## 🗑️ 卸载

```bash
# 卸载 FlintBloom
pip uninstall flintbloom

# 清理 Docker 资源
docker-compose down -v  # 警告：会删除数据！
```

---

## ❓ 常见问题

### Q1: 安装时出现依赖冲突怎么办？

A: 尝试在虚拟环境中安装：

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git
```

### Q2: 如何在离线环境安装？

A: 先下载源码和依赖：

```bash
# 在有网络的机器上
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom
pip download -r backend/requirements.txt -d ./packages

# 复制到离线机器后
pip install --no-index --find-links=./packages -e .
```

### Q3: 可以只复制客户端文件吗？

A: 可以！只需复制一个文件：

```bash
cp /path/to/FlintBloom/backend/flintbloom/callbacks.py your_project/
```

然后：

```python
from your_project.callbacks import FlintBloomCallbackHandler
```

### Q4: 如何在 Poetry 项目中使用？

A: 在 `pyproject.toml` 中添加：

```toml
[tool.poetry.dependencies]
flintbloom = {git = "https://github.com/zhangwenjiexbz/FlintBloom.git"}
```

### Q5: 如何在 Conda 环境中安装？

A:

```bash
conda create -n flintbloom python=3.11
conda activate flintbloom
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git
```

---

## 📚 下一步

安装完成后：

1. **客户端用户**：查看 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) 了解如何集成
2. **服务器部署**：查看 [README.md](README.md) 了解配置和使用
3. **开发者**：查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发流程

---

## 💡 推荐安装方式总结

| 使用场景 | 安装命令 | 说明 |
|---------|---------|------|
| 应用集成 | `pip install git+https://...` | 仅客户端，轻量级 |
| 本地开发 | `pip install -e .` | 可编辑模式 |
| 服务器部署 | `docker-compose up -d` | 完整服务 |
| 生产环境 | `pip install "...[server]"` | 服务器版本 |
| 参与开发 | `pip install -e ".[all]"` | 包含开发工具 |

选择适合你的方式，开始使用 FlintBloom！🌸
