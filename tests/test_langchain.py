from agenticemail.langchain import AgenticEmailToolkit


class FakeMessages:
    def __init__(self):
        self.sent = None

    def list(self, inbox_id):
        return [{"id": "msg_1"}]

    def send(self, inbox_id, to, subject, text=None, html=None):
        self.sent = {"inbox_id": inbox_id, "to": to, "subject": subject, "text": text}
        return {"id": "msg_1", "status": "sent"}

    def search(self, inbox_id, q=None):
        return [{"id": "msg_1", "q": q}]


class FakeInboxes:
    def list(self):
        return [{"id": "a@x"}]

    def create(self, username=None, domain=None):
        return {"id": f"{username}@{domain}"}


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()
        self.inboxes = FakeInboxes()


def test_exposes_expected_tools():
    toolkit = AgenticEmailToolkit(client=FakeClient())
    names = [fn.__name__ for fn in toolkit._tool_specs()]
    for expected in ["list_inboxes", "create_inbox", "send_email", "reply_to_message", "search_messages"]:
        assert expected in names


def test_send_email_tool_calls_the_client():
    client = FakeClient()
    toolkit = AgenticEmailToolkit(client=client)
    send_email = next(fn for fn in toolkit._tool_specs() if fn.__name__ == "send_email")
    result = send_email("a@x", ["b@y"], "Hi", text="yo")
    assert result["status"] == "sent"
    assert client.messages.sent["to"] == ["b@y"]


if __name__ == "__main__":
    test_exposes_expected_tools()
    test_send_email_tool_calls_the_client()
    print("ok")
