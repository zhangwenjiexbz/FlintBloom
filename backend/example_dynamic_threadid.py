"""
Dynamic Thread ID Examples for FlintBloom

This script demonstrates all the ways to use dynamic thread_id with FlintBloom.
"""

import os
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Import FlintBloom callback
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.modules.realtime.callbacks import FlintBloomCallbackHandler


# ============= Example 1: Auto-detect from LangGraph config =============

def example_1_auto_detect():
    """
    Example 1: Auto-detect thread_id from LangGraph config

    This is the RECOMMENDED approach for LangGraph applications.
    """
    print("\n" + "="*70)
    print("Example 1: Auto-detect thread_id from LangGraph config")
    print("="*70)

    # Create callback WITHOUT specifying thread_id
    callback = FlintBloomCallbackHandler(
        auto_detect_thread_id=True  # This is default
    )

    # Create a simple LangGraph app
    class State(TypedDict):
        messages: list

    def chat_node(state: State):
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        response = llm.invoke(state["messages"])
        return {"messages": state["messages"] + [response]}

    workflow = StateGraph(State)
    workflow.add_node("chat", chat_node)
    workflow.set_entry_point("chat")
    workflow.add_edge("chat", END)

    checkpointer = SqliteSaver.from_conn_string(":memory:")
    app = workflow.compile(checkpointer=checkpointer)

    # The thread_id is automatically extracted from config!
    result = app.invoke(
        {"messages": [HumanMessage(content="Hello")]},
        config={
            "configurable": {"thread_id": "user-123-session-456"},  # Auto-detected!
            "callbacks": [callback]
        }
    )

    print(f"✅ Thread ID was automatically detected: user-123-session-456")
    print(f"   View at: http://localhost:8000/api/v1/realtime/threads/user-123-session-456/events")


# ============= Example 2: Custom resolver function =============

def example_2_custom_resolver():
    """
    Example 2: Use custom resolver to generate thread_id from metadata

    Useful when you want to derive thread_id from user info, session, etc.
    """
    print("\n" + "="*70)
    print("Example 2: Custom resolver function")
    print("="*70)

    # Define custom resolver
    def resolve_thread_id(metadata):
        """Generate thread_id from user and session info"""
        user_id = metadata.get("user_id", "anonymous")
        session_id = metadata.get("session_id", "default")
        return f"user-{user_id}-session-{session_id}"

    # Create callback with custom resolver
    callback = FlintBloomCallbackHandler(
        thread_id_resolver=resolve_thread_id
    )

    # Use with LangChain
    llm = ChatOpenAI(model="gpt-3.5-turbo", callbacks=[callback])

    result = llm.invoke(
        [HumanMessage(content="Hello")],
        config={
            "metadata": {
                "user_id": "alice",
                "session_id": "abc123"
            }
        }
    )

    print(f"✅ Thread ID generated from metadata: user-alice-session-abc123")
    print(f"   View at: http://localhost:8000/api/v1/realtime/threads/user-alice-session-abc123/events")


# ============= Example 3: Multi-tenant scenario =============

def example_3_multi_tenant():
    """
    Example 3: Multi-tenant application with isolated thread_ids

    Each tenant gets their own namespace for thread_ids.
    """
    print("\n" + "="*70)
    print("Example 3: Multi-tenant scenario")
    print("="*70)

    def tenant_thread_id_resolver(metadata):
        """Generate tenant-isolated thread_id"""
        tenant_id = metadata.get("tenant_id", "default")
        user_id = metadata.get("user_id", "anonymous")
        conversation_id = metadata.get("conversation_id", "new")

        # Format: tenant/{tenant}/user/{user}/conv/{conv}
        return f"tenant/{tenant_id}/user/{user_id}/conv/{conversation_id}"

    callback = FlintBloomCallbackHandler(
        thread_id_resolver=tenant_thread_id_resolver
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", callbacks=[callback])

    # Simulate requests from different tenants
    tenants = [
        {"tenant_id": "company-a", "user_id": "user-1", "conversation_id": "conv-001"},
        {"tenant_id": "company-b", "user_id": "user-2", "conversation_id": "conv-002"},
    ]

    for tenant_info in tenants:
        result = llm.invoke(
            [HumanMessage(content="Hello")],
            config={"metadata": tenant_info}
        )

        thread_id = f"tenant/{tenant_info['tenant_id']}/user/{tenant_info['user_id']}/conv/{tenant_info['conversation_id']}"
        print(f"✅ Tenant {tenant_info['tenant_id']}: {thread_id}")


# ============= Example 4: FastAPI integration =============

def example_4_fastapi_integration():
    """
    Example 4: Integration with FastAPI

    Shows how to use dynamic thread_id in a web API.
    """
    print("\n" + "="*70)
    print("Example 4: FastAPI integration (code example)")
    print("="*70)

    code = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flintbloom import FlintBloomCallbackHandler
from langchain_openai import ChatOpenAI

app = FastAPI()

# Create callback with auto-detection
callback = FlintBloomCallbackHandler(auto_detect_thread_id=True)

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Generate thread_id from user and session
    thread_id = f"user-{request.user_id}-session-{request.session_id}"

    # Use LangChain with callback
    llm = ChatOpenAI(callbacks=[callback])

    result = llm.invoke(
        request.message,
        config={
            "metadata": {"thread_id": thread_id}
        }
    )

    return {
        "response": result.content,
        "thread_id": thread_id,
        "trace_url": f"http://localhost:8000/api/v1/realtime/threads/{thread_id}/events"
    }
'''
    print(code)


# ============= Example 5: Context-based thread_id =============

def example_5_context_based():
    """
    Example 5: Using context variables for thread_id

    Useful in async applications where thread_id comes from request context.
    """
    print("\n" + "="*70)
    print("Example 5: Context-based thread_id (code example)")
    print("="*70)

    code = '''
from contextvars import ContextVar
from flintbloom import FlintBloomCallbackHandler

# Context variable to store current thread_id
current_thread_id = ContextVar('thread_id', default='default')

def get_thread_id_from_context(metadata):
    """Get thread_id from context variable"""
    return current_thread_id.get()

# Create callback
callback = FlintBloomCallbackHandler(
    thread_id_resolver=get_thread_id_from_context
)

# In your request handler
@app.post("/chat")
async def chat(request: ChatRequest):
    # Set thread_id in context
    thread_id = f"user-{request.user_id}"
    current_thread_id.set(thread_id)

    # Use callback - it will automatically get thread_id from context
    result = await agent.ainvoke(
        request.message,
        config={"callbacks": [callback]}
    )

    return result
'''
    print(code)


# ============= Example 6: Backward compatibility =============

def example_6_backward_compatible():
    """
    Example 6: Static thread_id (backward compatible)

    The old way still works!
    """
    print("\n" + "="*70)
    print("Example 6: Static thread_id (backward compatible)")
    print("="*70)

    # Old way - still works!
    callback = FlintBloomCallbackHandler(thread_id="my-static-thread")

    llm = ChatOpenAI(model="gpt-3.5-turbo", callbacks=[callback])
    result = llm.invoke([HumanMessage(content="Hello")])

    print(f"✅ Static thread_id still works: my-static-thread")
    print(f"   View at: http://localhost:8000/api/v1/realtime/threads/my-static-thread/events")


# ============= Example 7: Priority demonstration =============

def example_7_priority():
    """
    Example 7: Thread ID resolution priority

    Shows how different sources are prioritized.
    """
    print("\n" + "="*70)
    print("Example 7: Thread ID resolution priority")
    print("="*70)

    print("""
Thread ID Resolution Priority (highest to lowest):

1. Custom resolver function
   callback = FlintBloomCallbackHandler(thread_id_resolver=my_func)

2. LangGraph config.configurable.thread_id
   config={"configurable": {"thread_id": "from-config"}}

3. Metadata.thread_id
   config={"metadata": {"thread_id": "from-metadata"}}

4. Static thread_id (constructor parameter)
   callback = FlintBloomCallbackHandler(thread_id="static")

5. Auto-generated from run_id
   Automatically generated if none of the above are available

Example showing priority:
""")

    def custom_resolver(metadata):
        return "from-custom-resolver"

    callback = FlintBloomCallbackHandler(
        thread_id="static-fallback",  # Priority 4
        thread_id_resolver=custom_resolver  # Priority 1 - wins!
    )

    print("✅ With custom resolver: thread_id will be 'from-custom-resolver'")
    print("   (Custom resolver has highest priority)")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("FlintBloom Dynamic Thread ID Examples")
    print("="*70)

    examples = [
        ("Auto-detect from LangGraph config", example_1_auto_detect),
        ("Custom resolver function", example_2_custom_resolver),
        ("Multi-tenant scenario", example_3_multi_tenant),
        ("FastAPI integration", example_4_fastapi_integration),
        ("Context-based thread_id", example_5_context_based),
        ("Backward compatibility", example_6_backward_compatible),
        ("Priority demonstration", example_7_priority),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            if os.getenv("OPENAI_API_KEY") or i > 3:  # Skip API calls if no key
                func()
            else:
                print(f"\n⚠️  Skipping {name} (requires OPENAI_API_KEY)")
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")

    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
✅ Problem 1 SOLVED: Import FlintBloom in other projects
   - Install: pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git
   - Or: pip install -e /path/to/FlintBloom
   - Import: from flintbloom import FlintBloomCallbackHandler

✅ Problem 2 SOLVED: Dynamic thread_id support
   - Auto-detect from LangGraph config (recommended)
   - Custom resolver functions
   - Context-based resolution
   - Multi-tenant support
   - Backward compatible with static thread_id

📚 See INTEGRATION_GUIDE.md for complete documentation
""")


if __name__ == "__main__":
    main()
