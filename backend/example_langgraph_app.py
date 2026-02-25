"""
Complete LangGraph Example with FlintBloom Integration

This example demonstrates how to build a simple agent with LangGraph
and integrate FlintBloom for observability.
"""

import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

# Import FlintBloom callback
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.modules.realtime.callbacks import FlintBloomCallbackHandler


# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Simulated web search
    return f"Search results for '{query}': Found relevant information about {query}."


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {e}"


# Define state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "The messages in the conversation"]
    next_action: str


# Define agent node
def agent_node(state: AgentState) -> AgentState:
    """Agent decision node"""
    messages = state["messages"]

    # Create LLM with tools
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools([search_web, calculate])

    # Get response
    response = llm_with_tools.invoke(messages)

    # Determine next action
    if response.tool_calls:
        next_action = "tools"
    else:
        next_action = "end"

    return {
        "messages": messages + [response],
        "next_action": next_action
    }


# Define tool node
def tool_node_func(state: AgentState) -> AgentState:
    """Execute tools"""
    messages = state["messages"]
    last_message = messages[-1]

    # Execute tools
    tool_node = ToolNode([search_web, calculate])
    tool_results = tool_node.invoke({"messages": [last_message]})

    return {
        "messages": messages + tool_results["messages"],
        "next_action": "agent"
    }


# Define routing function
def should_continue(state: AgentState) -> str:
    """Determine next node"""
    return state["next_action"]


def create_agent_graph():
    """Create the agent graph"""
    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node_func)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")

    # Add checkpointer
    checkpointer = SqliteSaver.from_conn_string("./data/example_checkpoints.db")

    # Compile
    app = workflow.compile(checkpointer=checkpointer)

    return app


def run_agent_with_flintbloom(query: str, thread_id: str = "example-thread"):
    """Run agent with FlintBloom tracking"""

    # Create FlintBloom callback
    callback = FlintBloomCallbackHandler(
        thread_id=thread_id,
        enable_streaming=True
    )

    # Create agent
    app = create_agent_graph()

    # Run agent
    print(f"\n{'='*60}")
    print(f"Running agent with query: {query}")
    print(f"Thread ID: {thread_id}")
    print(f"{'='*60}\n")

    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [callback]
    }

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next_action": "agent"
    }

    # Stream results
    for event in app.stream(initial_state, config):
        for node_name, node_output in event.items():
            print(f"\n--- {node_name} ---")
            if "messages" in node_output:
                last_message = node_output["messages"][-1]
                if isinstance(last_message, AIMessage):
                    print(f"AI: {last_message.content}")
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        print(f"Tool calls: {last_message.tool_calls}")

    print(f"\n{'='*60}")
    print("Agent execution complete!")
    print(f"View trace at: http://localhost:8000/api/v1/realtime/threads/{thread_id}/events")
    print(f"{'='*60}\n")

    return callback.get_run_summary()


def main():
    """Main function"""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Please set it to run this example.")
        print("   export OPENAI_API_KEY='your-api-key'")
        return

    # Example queries
    queries = [
        "What is 25 * 4 + 10?",
        "Search for information about LangGraph",
        "Calculate the square root of 144 and then search for information about that number"
    ]

    # Run examples
    for i, query in enumerate(queries, 1):
        thread_id = f"example-thread-{i}"
        summary = run_agent_with_flintbloom(query, thread_id)

        print(f"\nExecution Summary:")
        print(f"  Total runs: {summary['total_runs']}")
        print(f"  Thread ID: {summary['thread_id']}")

        input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    main()
