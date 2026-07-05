# API surface

Client: `AgenticEmail(api_key, base_url="https://app.agenticemail.dev")`. All methods return dicts (snake_case, as the API sends them) and raise `AgenticEmailError` on non-2xx responses.

## inboxes

- `client.inboxes.create(username=None, domain=None, display_name=None, client_id=None)`
- `client.inboxes.list(limit=None, page_token=None)`
- `client.inboxes.get(inbox_id)`
- `client.inboxes.update(inbox_id, display_name)`
- `client.inboxes.delete(inbox_id)`

## messages

- `client.messages.list(inbox_id, **filters)`
- `client.messages.search(inbox_id, q=None, **filters)`
- `client.messages.get(inbox_id, message_id)`
- `client.messages.raw(inbox_id, message_id)` → RFC 822 source string
- `client.messages.get_attachment(inbox_id, message_id, attachment_id)` → bytes
- `client.messages.send(inbox_id, to, subject, text=None, html=None, cc=None, bcc=None, attachments=None, labels=None, client_id=None)`
- `client.messages.send_batch(inbox_id, messages)`
- `client.messages.reply(inbox_id, message_id, text=None, html=None, to=None, cc=None, client_id=None)`
- `client.messages.forward(inbox_id, message_id, to, text=None, client_id=None)`
- `client.messages.update(inbox_id, message_id, add_labels=None, remove_labels=None)`

## threads

- `client.threads.list(inbox_id=None, **filters)` — omit `inbox_id` for org-wide
- `client.threads.search(q=None, inbox_id=None, **filters)`
- `client.threads.get(thread_id)`
- `client.threads.update(thread_id, add_labels=None, remove_labels=None)`

## drafts

- `client.drafts.create(inbox_id, **payload)` — supports `send_at` for scheduled send
- `client.drafts.list(inbox_id)`
- `client.drafts.get(inbox_id, draft_id)`
- `client.drafts.update(inbox_id, draft_id, **payload)`
- `client.drafts.delete(inbox_id, draft_id)`
- `client.drafts.send(inbox_id, draft_id)`

## lists (allow/block lists)

`direction` is `"receive" | "send" | "reply"`, `type` is `"allow" | "block"`; pass `inbox_id=None` for org-level lists.

- `client.lists.create(inbox_id, direction, type, entry, reason=None)`
- `client.lists.list(inbox_id, direction, type)`
- `client.lists.get(inbox_id, direction, type, entry)`
- `client.lists.delete(inbox_id, direction, type, entry)`

## webhooks

- `client.webhooks.create(url, event_types, inbox_ids=None)`
- `client.webhooks.list()`
- `client.webhooks.get(webhook_id)`
- `client.webhooks.delete(webhook_id)`
- `client.webhooks.deliveries(webhook_id)`

## domains

- `client.domains.create(domain, dns_connection_id=None, return_path=None, tracking_subdomain=None, open_tracking=None, click_tracking=None)`
- `client.domains.list()`
- `client.domains.get(domain_id)`
- `client.domains.verify(domain_id)`
- `client.domains.delete(domain_id)`

## api_keys

- `client.api_keys.create(name, scopes=None, scope_inbox_id=None)`
- `client.api_keys.list()`
- `client.api_keys.delete(api_key_id)`

## events

- `client.events.stream(inbox_ids=None, event_types=None)` — generator over the WebSocket feed (requires the `events` extra)

## Helpers

- `verify_webhook(body, headers, secret)` — validates the HMAC signature and returns the parsed event
- `AgenticEmailError` — `.status`, `.code`
- `agenticemail.langchain.AgenticEmailToolkit` — `from_api_key()`, `get_tools()` (requires the `langchain` extra)
