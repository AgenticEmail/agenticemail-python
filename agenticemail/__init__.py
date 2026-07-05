import base64
import hashlib
import hmac
import json
from typing import Any, Optional
from urllib.parse import quote

import httpx

__all__ = [
    "AgenticEmail",
    "AgenticEmailError",
    "AgentMail",
    "AgentMailError",
    "verify_webhook",
]


class AgenticEmailError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code


def _clean(data: Optional[dict]) -> Optional[dict]:
    if data is None:
        return None
    return {k: v for k, v in data.items() if v is not None}


def _enc(inbox_id: str) -> str:
    return quote(inbox_id, safe="")


class AgenticEmail:
    def __init__(self, api_key: str, base_url: str = "https://api.agenticemail.dev"):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        self.inboxes = _Inboxes(self)
        self.messages = _Messages(self)
        self.threads = _Threads(self)
        self.drafts = _Drafts(self)
        self.webhooks = _Webhooks(self)
        self.domains = _Domains(self)
        self.api_keys = _ApiKeys(self)
        self.lists = _Lists(self)
        self.events = _Events(self)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        raw: bool = False,
        binary: bool = False,
    ) -> Any:
        res = self._http.request(method, path, params=_clean(params), json=json_body)
        if res.status_code >= 400:
            code, message = "error", f"HTTP {res.status_code}"
            try:
                err = res.json()["error"]
                code, message = err["code"], err["message"]
            except Exception:
                pass
            raise AgenticEmailError(res.status_code, code, message)
        if res.status_code == 204:
            return None
        if raw:
            return res.text
        if binary:
            return res.content
        return res.json()


class _Inboxes:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def create(self, username=None, domain=None, display_name=None, client_id=None):
        return self._c._request(
            "POST",
            "/v1/inboxes",
            json_body=_clean(
                {"username": username, "domain": domain, "display_name": display_name, "client_id": client_id}
            ),
        )

    def list(self, limit=None, page_token=None):
        return self._c._request("GET", "/v1/inboxes", params={"limit": limit, "page_token": page_token})

    def get(self, inbox_id: str):
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}")

    def update(self, inbox_id: str, display_name):
        return self._c._request("PATCH", f"/v1/inboxes/{_enc(inbox_id)}", json_body={"display_name": display_name})

    def delete(self, inbox_id: str):
        return self._c._request("DELETE", f"/v1/inboxes/{_enc(inbox_id)}")


class _Messages:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def list(self, inbox_id: str, **filters):
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/messages", params=filters)

    def search(self, inbox_id: str, q=None, **filters):
        return self._c._request(
            "GET", f"/v1/inboxes/{_enc(inbox_id)}/messages/search", params={"q": q, **filters}
        )

    def get(self, inbox_id: str, message_id: str):
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}")

    def update(self, inbox_id: str, message_id: str, add_labels=None, remove_labels=None):
        return self._c._request(
            "PATCH",
            f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}",
            json_body=_clean({"add_labels": add_labels, "remove_labels": remove_labels}),
        )

    def raw(self, inbox_id: str, message_id: str) -> str:
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}/raw", raw=True)

    def get_attachment(self, inbox_id: str, message_id: str, attachment_id: str) -> bytes:
        return self._c._request(
            "GET",
            f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}/attachments/{attachment_id}",
            binary=True,
        )

    def send(self, inbox_id: str, to, subject, text=None, html=None, cc=None, bcc=None, attachments=None, labels=None, client_id=None):
        return self._c._request(
            "POST",
            f"/v1/inboxes/{_enc(inbox_id)}/messages/send",
            json_body=_clean(
                {
                    "to": to,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": subject,
                    "text": text,
                    "html": html,
                    "attachments": attachments,
                    "labels": labels,
                    "client_id": client_id,
                }
            ),
        )

    def send_batch(self, inbox_id: str, messages: list):
        return self._c._request(
            "POST", f"/v1/inboxes/{_enc(inbox_id)}/messages/batch", json_body={"messages": messages}
        )

    def reply(self, inbox_id: str, message_id: str, text=None, html=None, to=None, cc=None, client_id=None):
        return self._c._request(
            "POST",
            f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}/reply",
            json_body=_clean({"text": text, "html": html, "to": to, "cc": cc, "client_id": client_id}),
        )

    def forward(self, inbox_id: str, message_id: str, to, text=None, client_id=None):
        return self._c._request(
            "POST",
            f"/v1/inboxes/{_enc(inbox_id)}/messages/{message_id}/forward",
            json_body=_clean({"to": to, "text": text, "client_id": client_id}),
        )


class _Threads:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def list(self, inbox_id: Optional[str] = None, **filters):
        if inbox_id:
            return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/threads", params=filters)
        return self._c._request("GET", "/v1/threads", params=filters)

    def search(self, q=None, inbox_id: Optional[str] = None, **filters):
        params = {"q": q, **filters}
        if inbox_id:
            return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/threads/search", params=params)
        return self._c._request("GET", "/v1/threads/search", params=params)

    def get(self, thread_id: str):
        return self._c._request("GET", f"/v1/threads/{thread_id}")

    def update(self, thread_id: str, add_labels=None, remove_labels=None):
        return self._c._request(
            "PATCH",
            f"/v1/threads/{thread_id}",
            json_body=_clean({"add_labels": add_labels, "remove_labels": remove_labels}),
        )


class _Lists:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def _path(self, inbox_id, direction, type):
        if inbox_id:
            return f"/v1/inboxes/{_enc(inbox_id)}/lists/{direction}/{type}"
        return f"/v1/lists/{direction}/{type}"

    def create(self, inbox_id, direction, type, entry, reason=None):
        return self._c._request(
            "POST", self._path(inbox_id, direction, type), json_body=_clean({"entry": entry, "reason": reason})
        )

    def list(self, inbox_id, direction, type):
        return self._c._request("GET", self._path(inbox_id, direction, type))

    def get(self, inbox_id, direction, type, entry):
        return self._c._request("GET", f"{self._path(inbox_id, direction, type)}/{_enc(entry)}")

    def delete(self, inbox_id, direction, type, entry):
        return self._c._request("DELETE", f"{self._path(inbox_id, direction, type)}/{_enc(entry)}")


class _Drafts:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def create(self, inbox_id: str, **payload):
        return self._c._request("POST", f"/v1/inboxes/{_enc(inbox_id)}/drafts", json_body=_clean(payload))

    def list(self, inbox_id: str):
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/drafts")

    def get(self, inbox_id: str, draft_id: str):
        return self._c._request("GET", f"/v1/inboxes/{_enc(inbox_id)}/drafts/{draft_id}")

    def update(self, inbox_id: str, draft_id: str, **payload):
        return self._c._request("PATCH", f"/v1/inboxes/{_enc(inbox_id)}/drafts/{draft_id}", json_body=_clean(payload))

    def delete(self, inbox_id: str, draft_id: str):
        return self._c._request("DELETE", f"/v1/inboxes/{_enc(inbox_id)}/drafts/{draft_id}")

    def send(self, inbox_id: str, draft_id: str):
        return self._c._request("POST", f"/v1/inboxes/{_enc(inbox_id)}/drafts/{draft_id}/send")


class _Webhooks:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def create(self, url: str, event_types, inbox_ids=None):
        return self._c._request(
            "POST", "/v1/webhooks", json_body=_clean({"url": url, "event_types": event_types, "inbox_ids": inbox_ids})
        )

    def list(self):
        return self._c._request("GET", "/v1/webhooks")

    def get(self, webhook_id: str):
        return self._c._request("GET", f"/v1/webhooks/{webhook_id}")

    def delete(self, webhook_id: str):
        return self._c._request("DELETE", f"/v1/webhooks/{webhook_id}")

    def deliveries(self, webhook_id: str):
        return self._c._request("GET", f"/v1/webhooks/{webhook_id}/deliveries")


class _Domains:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def create(
        self,
        domain: str,
        dns_connection_id=None,
        return_path=None,
        tracking_subdomain=None,
        open_tracking=None,
        click_tracking=None,
    ):
        return self._c._request(
            "POST",
            "/v1/domains",
            json_body=_clean(
                {
                    "domain": domain,
                    "dns_connection_id": dns_connection_id,
                    "return_path": return_path,
                    "tracking_subdomain": tracking_subdomain,
                    "open_tracking": open_tracking,
                    "click_tracking": click_tracking,
                }
            ),
        )

    def list(self):
        return self._c._request("GET", "/v1/domains")

    def get(self, domain_id: str):
        return self._c._request("GET", f"/v1/domains/{domain_id}")

    def verify(self, domain_id: str):
        return self._c._request("POST", f"/v1/domains/{domain_id}/verify")

    def delete(self, domain_id: str):
        return self._c._request("DELETE", f"/v1/domains/{domain_id}")


class _ApiKeys:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def create(self, name: str, scopes=None, scope_inbox_id=None):
        return self._c._request(
            "POST",
            "/v1/api-keys",
            json_body=_clean({"name": name, "scopes": scopes, "scope_inbox_id": scope_inbox_id}),
        )

    def list(self):
        return self._c._request("GET", "/v1/api-keys")

    def delete(self, api_key_id: str):
        return self._c._request("DELETE", f"/v1/api-keys/{api_key_id}")


class _Events:
    def __init__(self, c: AgenticEmail):
        self._c = c

    def stream(self, inbox_ids=None, event_types=None):
        try:
            from websocket import create_connection
        except ImportError as exc:
            raise AgenticEmailError(0, "no_websocket", "Install websocket-client to use events") from exc
        ws_url = self._c._base_url.replace("http", "ws", 1) + "/v1/events?token=" + quote(self._c._api_key, safe="")
        ws = create_connection(ws_url)
        ws.send(json.dumps({"type": "subscribe", "inbox_ids": inbox_ids, "event_types": event_types}))
        try:
            while True:
                raw = ws.recv()
                if not raw:
                    break
                msg = json.loads(raw)
                if msg.get("event_id") and msg.get("type"):
                    yield msg
        finally:
            ws.close()


def verify_webhook(body: str, headers: dict, secret: str) -> dict:
    wid = headers.get("webhook-id")
    ts = headers.get("webhook-timestamp")
    sig_header = headers.get("webhook-signature")
    if not wid or not ts or not sig_header:
        raise AgenticEmailError(400, "invalid_signature", "Missing webhook signature headers")

    # Secrets are base64url and unpadded (whsec_ + 24 random bytes); accept
    # both alphabets like the server's Node decoder does.
    key_b64 = secret[6:] if secret.startswith("whsec_") else secret
    key_b64 = key_b64.replace("-", "+").replace("_", "/")
    key = base64.b64decode(key_b64 + "=" * (-len(key_b64) % 4))
    expected = base64.b64encode(
        hmac.new(key, f"{wid}.{ts}.{body}".encode(), hashlib.sha256).digest()
    ).decode()
    for token in sig_header.split(" "):
        parts = token.split(",")
        if len(parts) == 2 and hmac.compare_digest(parts[1], expected):
            return json.loads(body)
    raise AgenticEmailError(400, "invalid_signature", "Webhook signature verification failed")

# Deprecated aliases — kept for backward compatibility.
AgentMail = AgenticEmail
AgentMailError = AgenticEmailError
