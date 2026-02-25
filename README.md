# FlintBloom

**AI Observability Platform for LangChain & LangGraph**

Open-source alternative to LangSmith with local deployment support. Monitor, debug, and optimize your LangChain/LangGraph applications with powerful trace visualization and analytics.

## ✨ Features

### 🔍 Offline Analysis Mode
- **Checkpoint-based Analysis**: Read from LangGraph's checkpoint tables (CheckpointBlobs, CheckpointWrites, Checkpoints)
- **Zero Runtime Overhead**: Analyze historical data without modifying your application
- **Time Travel Debugging**: Replay and inspect any checkpoint state
- **Deep Insights**: Extract execution traces, token usage, and performance metrics

### ⚡ Real-time Tracking Mode
- **Live Monitoring**: Stream execution events via WebSocket
- **Custom Callbacks**: Drop-in LangChain callback handler
- **Event Buffering**: Capture and replay events
- **Real-time Metrics**: Track token usage and costs as they happen

### 🗄️ Multi-Database Support
- **MySQL** - Production-ready with full JSON support
- **PostgreSQL** - Advanced JSONB queries and indexing
- **SQLite** - Lightweight local development

### 📊 Visualization & Analytics
- Execution trace graphs
- Token usage and cost analysis
- Performance metrics and bottleneck detection
- Checkpoint comparison
- Thread timeline view

## 🚀 Quick Start

### Option 1: Install Client Only (For Application Integration)

If you just want to add FlintBloom observability to your existing application:

```bash
# Install from GitHub
pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git

# Or install locally in development mode
cd /path/to/FlintBloom
pip install -e .
```

Then use in your code:

```python
from flintbloom import FlintBloomCallbackHandler
from langchain_openai import ChatOpenAI

# Create callback with auto-detect thread_id
callback = FlintBloomCallbackHandler()

# Use with LangChain
llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Hello!")
```

**See [INSTALL.md](INSTALL.md) for detailed installation options.**

### Option 2: Deploy Full Server (Using Docker Compose)

To run the complete FlintBloom server with database and API:

```bash
# Clone the repository
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom

# Copy environment file
cp .env.example .env

# Edit .env to configure your database
# DB_TYPE=mysql  # or postgresql, sqlite

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

The API will be available at `http://localhost:8000`

### Option 3: Manual Server Installation

```bash
# Install server dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your database settings

# Run the application
python -m app.main
```

## 📖 Usage

### 1. Offline Analysis Mode

Analyze existing LangGraph checkpoint data:

```python
import requests

# List all threads
response = requests.get("http://localhost:8000/api/v1/offline/threads")
threads = response.json()

# Get checkpoints for a thread
thread_id = "your-thread-id"
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/checkpoints")
checkpoints = response.json()

# Get detailed trace
checkpoint_id = "checkpoint-id"
response = requests.get(
    f"http://localhost:8000/api/v1/offline/threads/{thread_id}/checkpoints/{checkpoint_id}/trace"
)
trace = response.json()

# Analyze entire thread
response = requests.get(f"http://localhost:8000/api/v1/offline/threads/{thread_id}/analysis")
analysis = response.json()
```

### 2. Real-time Tracking Mode

Add FlintBloom callback to your LangChain/LangGraph application:

#### Option A: Auto-detect thread_id (Recommended for LangGraph)

```python
from flintbloom import FlintBloomCallbackHandler

# Create callback without specifying thread_id
callback = FlintBloomCallbackHandler()

# Use with LangGraph - thread_id is auto-detected from config!
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

graph = StateGraph(YourState)
# ... build your graph ...
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = graph.compile(checkpointer=checkpointer)

result = app.invoke(
    {"input": "your input"},
    config={
        "configurable": {"thread_id": "user-123-session-456"},  # Auto-detected!
        "callbacks": [callback]
    }
)
```

#### Option B: Custom thread_id resolver

```python
from flintbloom import FlintBloomCallbackHandler

# Define custom resolver
def resolve_thread_id(metadata):
    user_id = metadata.get("user_id", "anonymous")
    session_id = metadata.get("session_id", "default")
    return f"user-{user_id}-session-{session_id}"

# Create callback with custom resolver
callback = FlintBloomCallbackHandler(
    thread_id_resolver=resolve_thread_id
)

# Use with LangChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke(
    "Explain quantum computing",
    config={
        "metadata": {
            "user_id": "alice",
            "session_id": "abc123"
        }
    }
)
# Thread ID will be: user-alice-session-abc123
```

#### Option C: Static thread_id (Simple cases)

```python
from flintbloom import FlintBloomCallbackHandler

# Static thread_id (backward compatible)
callback = FlintBloomCallbackHandler(thread_id="my-static-thread")

llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Hello")
```

**See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for more examples and best practices.**

### 3. WebSocket Real-time Streaming

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws/my-thread-123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'event') {
        console.log('New event:', data.data);
        // Update your UI with the event
    }
};

ws.onopen = () => {
    console.log('Connected to FlintBloom');
};
```

## 🏗️ Architecture

```
FlintBloom/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── core/              # Configuration & Database
│   │   ├── db/                # Models, Schemas, Adapters
│   │   │   └── adapters/      # MySQL, PostgreSQL, SQLite
│   │   ├── modules/
│   │   │   ├── offline/       # Checkpoint Analysis
│   │   │   └── realtime/      # Live Tracking
│   │   └── main.py            # FastAPI App
│   └── requirements.txt
├── frontend/                   # React Frontend (TBD)
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Database Type
DB_TYPE=mysql  # mysql, postgresql, or sqlite

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=agentnext

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=agentnext

# SQLite Configuration
SQLITE_PATH=./data/flintbloom.db

# Real-time Features
ENABLE_REALTIME=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Offline Analysis
- `GET /api/v1/offline/threads` - List all threads
- `GET /api/v1/offline/threads/{thread_id}/checkpoints` - List checkpoints
- `GET /api/v1/offline/threads/{thread_id}/checkpoints/{checkpoint_id}/trace` - Get trace
- `GET /api/v1/offline/threads/{thread_id}/analysis` - Analyze thread
- `GET /api/v1/offline/threads/{thread_id}/timeline` - Get timeline

#### Real-time Tracking
- `WS /api/v1/realtime/ws/{thread_id}` - WebSocket stream
- `GET /api/v1/realtime/threads` - List active threads
- `GET /api/v1/realtime/threads/{thread_id}/events` - Get buffered events
- `GET /api/v1/realtime/threads/{thread_id}/summary` - Get summary

## 🎯 Roadmap

- [x] Core backend architecture
- [x] Multi-database support (MySQL, PostgreSQL, SQLite)
- [x] Offline checkpoint analysis
- [x] Real-time tracking with callbacks
- [x] WebSocket streaming
- [ ] React frontend with trace visualization
- [ ] Checkpoint replay functionality
- [ ] Advanced cost optimization suggestions
- [ ] Prompt version management
- [ ] Team collaboration features
- [ ] Export/import functionality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built for the LangChain/LangGraph community as an open-source alternative to LangSmith.

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/zhangwenjiexbz/FlintBloom/issues)
- Documentation: [Full docs](https://github.com/zhangwenjiexbz/FlintBloom/wiki)
