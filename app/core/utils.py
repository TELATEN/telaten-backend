import json
from typing import Any

def format_sse(event_type: str, message: str | None = None, data: dict | Any | None = None) -> str:
    """
    Formats a Server-Sent Event (SSE) message string.
    
    Args:
        event_type: The type of event (e.g., 'progress', 'token', 'error').
        message: Optional human-readable message.
        data: Optional data payload (will be JSON serialized).
    
    Returns:
        A string formatted as an SSE message: "data: {...}\n\n"
    """
    payload: dict[str, Any] = {"type": event_type}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
        
    return f"data: {json.dumps(payload)}\n\n"
