"""LangChain integration for AgenticEmail.

Wraps the AgenticEmail SDK as LangChain tools, mirroring AgenticEmail's
``langchain-agentmail`` package::

    from agenticemail.langchain import AgenticEmailToolkit

    toolkit = AgenticEmailToolkit.from_api_key()
    tools = toolkit.get_tools()

For TypeScript/JavaScript agent frameworks (Vercel AI SDK, OpenAI Agents,
Claude Agent SDK), point the framework at the built-in MCP server at ``/mcp``
instead. MCP is the framework-agnostic tool bridge, so it needs no separate
per-framework wrapper.
"""

import os
from typing import List, Optional

from . import AgenticEmail


class AgenticEmailToolkit:
    def __init__(
        self,
        client: Optional[AgenticEmail] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        if client is None:
            key = api_key or os.environ.get("AGENTICEMAIL_API_KEY")
            if not key:
                raise ValueError("Provide a client, an api_key, or set AGENTICEMAIL_API_KEY")
            client = AgenticEmail(key, base_url) if base_url else AgenticEmail(key)
        self.client = client

    @classmethod
    def from_api_key(cls, api_key: Optional[str] = None, base_url: Optional[str] = None) -> "AgenticEmailToolkit":
        return cls(api_key=api_key, base_url=base_url)

    def _tool_specs(self):
        c = self.client

        def list_inboxes() -> list:
            """List the inboxes available to this agent."""
            return c.inboxes.list()

        def create_inbox(username: Optional[str] = None, domain: Optional[str] = None) -> dict:
            """Create a new inbox, optionally with a username and domain."""
            return c.inboxes.create(username=username, domain=domain)

        def list_messages(inbox_id: str) -> list:
            """List the messages in an inbox."""
            return c.messages.list(inbox_id)

        def get_message(inbox_id: str, message_id: str) -> dict:
            """Fetch a single message by id."""
            return c.messages.get(inbox_id, message_id)

        def send_email(
            inbox_id: str,
            to: List[str],
            subject: str,
            text: Optional[str] = None,
            html: Optional[str] = None,
        ) -> dict:
            """Send an email from an inbox to one or more recipients."""
            return c.messages.send(inbox_id, to, subject, text=text, html=html)

        def reply_to_message(inbox_id: str, message_id: str, text: str) -> dict:
            """Reply to a message, keeping it in the same thread."""
            return c.messages.reply(inbox_id, message_id, text=text)

        def search_messages(inbox_id: str, query: str) -> list:
            """Full-text search the messages in an inbox."""
            return c.messages.search(inbox_id, q=query)

        return [
            list_inboxes,
            create_inbox,
            list_messages,
            get_message,
            send_email,
            reply_to_message,
            search_messages,
        ]

    def get_tools(self):
        try:
            from langchain_core.tools import StructuredTool
        except ImportError as exc:
            raise ImportError("Install langchain-core to use get_tools()") from exc
        return [StructuredTool.from_function(fn) for fn in self._tool_specs()]


# Deprecated alias — kept for backward compatibility.
AgentMailToolkit = AgenticEmailToolkit
