from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import asyncio
import json
from app.modules.realtime.collector import get_global_collector
from app.modules.realtime.callbacks import FlintBloomCallbackHandler

router = APIRouter(prefix="/realtime", tags=["Real-time Tracking"])


@router.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """
    WebSocket endpoint for real-time event streaming

    Args:
        websocket: WebSocket connection
        thread_id: Thread identifier to subscribe to

    Usage:
        const ws = new WebSocket('ws://localhost:8000/realtime/ws/thread-123');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Event:', data);
        };
    """
    await websocket.accept()
    collector = get_global_collector()
    queue = collector.subscribe(thread_id)

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "message": f"Connected to thread {thread_id}",
            "thread_id": thread_id,
        })

        # Send buffered events
        buffered_events = collector.get_events(thread_id)
        if buffered_events:
            await websocket.send_json({
                "type": "buffered_events",
                "events": buffered_events,
                "count": len(buffered_events),
            })

        # Stream new events
        while True:
            try:
                # Wait for new event with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json({
                    "type": "event",
                    "data": event,
                })
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": asyncio.get_event_loop().time(),
                })

    except WebSocketDisconnect:
        collector.unsubscribe(thread_id, queue)
    except Exception as e:
        collector.unsubscribe(thread_id, queue)
        await websocket.close(code=1011, reason=str(e))


@router.get("/threads")
async def list_active_threads():
    """
    List all threads with active real-time tracking

    Returns:
        List of active thread IDs
    """
    collector = get_global_collector()
    threads = collector.get_active_threads()

    return {
        "threads": threads,
        "count": len(threads),
    }


@router.get("/threads/{thread_id}/events")
async def get_thread_events(
    thread_id: str,
    limit: Optional[int] = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """
    Get buffered events for a thread

    Args:
        thread_id: Thread identifier
        limit: Maximum number of events to return
        offset: Number of events to skip

    Returns:
        List of events
    """
    collector = get_global_collector()
    events = collector.get_events(thread_id, limit, offset)
    total = collector.get_event_count(thread_id)

    return {
        "thread_id": thread_id,
        "events": events,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/threads/{thread_id}/summary")
async def get_thread_summary(thread_id: str):
    """
    Get summary statistics for a thread

    Args:
        thread_id: Thread identifier

    Returns:
        Summary statistics
    """
    collector = get_global_collector()
    summary = collector.get_summary(thread_id)

    if summary["event_count"] == 0:
        raise HTTPException(status_code=404, detail="Thread not found or no events")

    return summary


@router.delete("/threads/{thread_id}/events")
async def clear_thread_events(thread_id: str):
    """
    Clear all buffered events for a thread

    Args:
        thread_id: Thread identifier

    Returns:
        Success message
    """
    collector = get_global_collector()
    collector.clear_events(thread_id)

    return {
        "message": f"Events cleared for thread {thread_id}",
        "thread_id": thread_id,
    }


@router.get("/threads/{thread_id}/export")
async def export_thread_events(
    thread_id: str,
    format: str = Query(default="json", regex="^(json|jsonl)$"),
):
    """
    Export events for a thread

    Args:
        thread_id: Thread identifier
        format: Export format (json or jsonl)

    Returns:
        Exported events as string
    """
    collector = get_global_collector()

    try:
        exported = collector.export_events(thread_id, format)
        return {
            "thread_id": thread_id,
            "format": format,
            "data": exported,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/callback/create")
async def create_callback_handler(
    thread_id: str,
    enable_streaming: bool = Query(default=True),
):
    """
    Create a new callback handler instance

    Args:
        thread_id: Thread identifier
        enable_streaming: Whether to enable real-time streaming

    Returns:
        Instructions for using the callback handler
    """
    return {
        "thread_id": thread_id,
        "enable_streaming": enable_streaming,
        "usage": {
            "python": f"""
from app.modules.realtime.callbacks import FlintBloomCallbackHandler

# Create callback handler
callback = FlintBloomCallbackHandler(
    thread_id="{thread_id}",
    enable_streaming={enable_streaming}
)

# Use with LangChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("Hello!")

# Use with LangGraph
from langgraph.graph import StateGraph

graph = StateGraph(...)
app = graph.compile()
result = app.invoke(
    input_data,
    config={{"callbacks": [callback]}}
)
            """.strip(),
        },
        "websocket_url": f"ws://localhost:8000/realtime/ws/{thread_id}",
    }
