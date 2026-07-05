# AgenticEmail Python SDK

The official Python library for the [AgenticEmail](https://agenticemail.dev) API — programmatic inboxes, send and receive email, webhooks, and real-time events for AI agents.

## Installation

```bash
pip install agenticemail
```

Optional extras: `agenticemail[events]` (WebSocket event stream), `agenticemail[langchain]` (LangChain toolkit).

## Usage

```python
import os
from agenticemail import AgenticEmail

client = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])

# Give your agent an inbox in one call
inbox = client.inboxes.create(username="support", domain="acme.io")

# Send
client.messages.send(
    inbox["id"],
    to=["customer@example.com"],
    subject="Hello",
    text="Sent from an agent.",
)

# Read
threads = client.threads.list(inbox["id"])
```

Responses are plain dicts in the API's snake_case. Get an API key from the [dashboard](https://app.agenticemail.dev/keys).

## Real-time events

Requires the `events` extra (`websocket-client`):

```python
for event in client.events.stream(event_types=["message.received"]):
    print(event["type"], event["data"])
```

## Webhook verification

```python
from agenticemail import verify_webhook

event = verify_webhook(raw_body, request.headers, os.environ["WEBHOOK_SECRET"])
if event["type"] == "message.received":
    ...
```

`verify_webhook` raises `AgenticEmailError` when the signature is invalid.

## LangChain toolkit

```python
from agenticemail.langchain import AgenticEmailToolkit

tools = AgenticEmailToolkit.from_api_key().get_tools()  # reads AGENTICEMAIL_API_KEY
```

## Error handling

All non-2xx responses raise `AgenticEmailError` with `.status`, `.code`, and a message:

```python
from agenticemail import AgenticEmailError

try:
    client.inboxes.get("missing")
except AgenticEmailError as err:
    print(err.status, err.code)
```

## Self-hosted

```python
client = AgenticEmail(api_key="am_...", base_url="https://your-agenticemail-host")
```

## API surface

See [api.md](./api.md) for every resource and method: `inboxes`, `messages`, `threads`, `drafts`, `lists`, `webhooks`, `domains`, `api_keys`, `events`.

## Requirements

Python 3.9+. Fully type-annotated (`py.typed`).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). This repo is an exported snapshot of the SDK developed in the AgenticEmail monorepo.

## License

[Apache-2.0](./LICENSE)
