"""
FlintBloom Usage Examples

This script demonstrates how to use FlintBloom for both offline analysis
and real-time tracking of LangChain/LangGraph applications.
"""

import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.modules.realtime.callbacks import FlintBloomCallbackHandler
from app.modules.realtime.collector import get_global_collector
import requests


def example_realtime_tracking():
    """Example: Real-time tracking with LangChain"""
    print("=" * 60)
    print("Example 1: Real-time Tracking")
    print("=" * 60)

    # Create callback handler
    thread_id = "example-thread-001"
    callback = FlintBloomCallbackHandler(
        thread_id=thread_id,
        enable_streaming=True
    )

    # Use with LangChain
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        callbacks=[callback]
    )

    print(f"\n🚀 Running LLM with thread_id: {thread_id}")
    result = llm.invoke([HumanMessage(content="What is 2+2?")])
    print(f"✅ Result: {result.content}")

    # Get summary
    collector = get_global_collector()
    summary = collector.get_summary(thread_id)

    print(f"\n📊 Summary:")
    print(f"  - Events captured: {summary['event_count']}")
    print(f"  - Event types: {summary['event_types']}")
    print(f"  - Total tokens: {summary['total_tokens']}")
    print(f"  - Duration: {summary['duration_ms']:.2f}ms")

    return thread_id


def example_offline_analysis():
    """Example: Offline analysis of checkpoint data"""
    print("\n" + "=" * 60)
    print("Example 2: Offline Analysis")
    print("=" * 60)

    base_url = "http://localhost:8000/api/v1/offline"

    # List threads
    print("\n📋 Listing threads...")
    response = requests.get(f"{base_url}/threads?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} threads")
        for thread in data['threads'][:3]:
            print(f"  - {thread['thread_id']}: {thread['checkpoint_count']} checkpoints")

        # Analyze first thread if available
        if data['threads']:
            thread_id = data['threads'][0]['thread_id']
            print(f"\n🔍 Analyzing thread: {thread_id}")

            response = requests.get(f"{base_url}/threads/{thread_id}/analysis")
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Analysis complete:")
                print(f"  - Checkpoints: {analysis['checkpoint_count']}")
                print(f"  - Total tokens: {analysis['total_tokens']}")
                print(f"  - Total cost: ${analysis['total_cost']:.4f}")
                print(f"  - Total duration: {analysis['total_duration_ms']:.2f}ms")
    else:
        print(f"❌ Failed to fetch threads: {response.status_code}")


def example_websocket_streaming():
    """Example: WebSocket streaming (requires asyncio)"""
    print("\n" + "=" * 60)
    print("Example 3: WebSocket Streaming")
    print("=" * 60)

    print("""
To use WebSocket streaming, connect from your frontend:

JavaScript Example:
-------------------
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws/your-thread-id');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data);
};

ws.onopen = () => {
    console.log('Connected to FlintBloom');
};

Python Example:
--------------
import asyncio
import websockets
import json

async def stream_events(thread_id):
    uri = f"ws://localhost:8000/api/v1/realtime/ws/{thread_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Event: {data}")

asyncio.run(stream_events("your-thread-id"))
    """)


def example_langgraph_integration():
    """Example: LangGraph integration"""
    print("\n" + "=" * 60)
    print("Example 4: LangGraph Integration")
    print("=" * 60)

    print("""
To use FlintBloom with LangGraph:

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.modules.realtime.callbacks import FlintBloomCallbackHandler

# Define your state
class AgentState(TypedDict):
    messages: list

# Create callback
callback = FlintBloomCallbackHandler(
    thread_id="langgraph-example",
    enable_streaming=True
)

# Build graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

# Add edges
graph.add_edge("agent", "tools")
graph.add_edge("tools", "agent")

# Set entry point
graph.set_entry_point("agent")

# Compile with checkpointer
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Run with callback
result = app.invoke(
    {"messages": [HumanMessage(content="Hello")]},
    config={
        "callbacks": [callback],
        "configurable": {"thread_id": "langgraph-example"}
    }
)
    """)


def main():
    """Run all examples"""
    print("\n🌟 FlintBloom Usage Examples 🌟\n")

    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ FlintBloom API is running\n")
        else:
            print("⚠️  FlintBloom API returned unexpected status\n")
    except requests.exceptions.RequestException:
        print("❌ FlintBloom API is not running!")
        print("   Please start it with: docker-compose up -d")
        print("   Or run: python -m app.main\n")
        return

    # Run examples
    try:
        # Example 1: Real-time tracking (requires OpenAI API key)
        # Uncomment if you have OPENAI_API_KEY set
        # thread_id = example_realtime_tracking()

        # Example 2: Offline analysis
        example_offline_analysis()

        # Example 3: WebSocket info
        example_websocket_streaming()

        # Example 4: LangGraph info
        example_langgraph_integration()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✨ Examples complete!")
    print("=" * 60)
    print("\n📚 For more information, visit: http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
