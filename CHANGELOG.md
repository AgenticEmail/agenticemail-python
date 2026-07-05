# Changelog

## 0.1.0

Initial public release.

- `AgenticEmail` client covering inboxes, messages (send, batch, reply, forward, search, attachments, raw), threads, drafts (including scheduled send), allow/block lists, webhooks, domains, and API keys
- Real-time event stream over WebSocket (`client.events.stream`, `events` extra)
- `verify_webhook` HMAC signature verification helper
- LangChain toolkit (`agenticemail.langchain.AgenticEmailToolkit`, `langchain` extra)
- Type-annotated with `py.typed`; single runtime dependency (`httpx`)
