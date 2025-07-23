# core_mcp/mcp.py

from typing import Dict, Any, Optional
import uuid
import json

class MCPMessage:
    """
    Message class for Model Context Protocol (MCP) used for agent communication in agentic RAG systems.
    Standardizes message structure and payload for multi-format document QA.
    """
    # Message type constants
    TYPE_INGEST = "ingest"
    TYPE_INDEX = "index"
    TYPE_RETRIEVE = "retrieve"
    TYPE_GENERATE = "generate"
    TYPE_ANSWER = "answer"
    TYPE_ERROR = "error"

    def __init__(
        self,
        sender: str,
        receiver: str,
        msg_type: str,
        payload: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        """
        Initialize an MCPMessage.
        Args:
            sender: Name of the sending agent/component.
            receiver: Name of the receiving agent/component.
            msg_type: Type of message (use class constants).
            payload: Message content (should follow schema for msg_type).
            trace_id: Optional unique identifier for tracing (auto-generated if not provided).
        """
        self.sender = sender
        self.receiver = receiver
        self.type = msg_type
        self.trace_id = trace_id or str(uuid.uuid4())
        self.payload = payload
        self._validate()

    def _validate(self):
        """
        Basic validation for required fields in payload based on message type.
        Extend this as needed for stricter schema enforcement.
        """
        if not isinstance(self.payload, dict):
            raise ValueError("Payload must be a dictionary.")
        if self.type == self.TYPE_INGEST:
            if "doc_type" not in self.payload or "file_path" not in self.payload:
                raise ValueError("Ingest payload must include 'doc_type' and 'file_path'.")
        elif self.type == self.TYPE_INDEX:
            if "chunks" not in self.payload or "embeddings" not in self.payload:
                raise ValueError("Index payload must include 'chunks' and 'embeddings'.")
        elif self.type == self.TYPE_RETRIEVE:
            if "query" not in self.payload:
                raise ValueError("Retrieve payload must include 'query'.")
        elif self.type == self.TYPE_GENERATE:
            if "question" not in self.payload or "context" not in self.payload:
                raise ValueError("Generate payload must include 'question' and 'context'.")
        elif self.type == self.TYPE_ANSWER:
            if "answer" not in self.payload:
                raise ValueError("Answer payload must include 'answer'.")
        elif self.type == self.TYPE_ERROR:
            if "error" not in self.payload:
                raise ValueError("Error payload must include 'error'.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

    def to_json(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MCPMessage":
        """Create an MCPMessage from a dictionary."""
        return MCPMessage(
            sender=data["sender"],
            receiver=data["receiver"],
            msg_type=data["type"],
            trace_id=data.get("trace_id"),
            payload=data["payload"]
        )

    @staticmethod
    def from_json(data: str) -> "MCPMessage":
        """Create an MCPMessage from a JSON string."""
        return MCPMessage.from_dict(json.loads(data))
