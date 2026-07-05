"""A minimal auto-reply agent.

Polls an inbox and replies once to every inbound message.

    export AGENTICEMAIL_API_KEY=am_...
    export AGENTICEMAIL_INBOX=support@yourdomain.com
    export AGENTICEMAIL_BASE_URL=http://localhost:3000   # omit for the hosted API
    python examples/auto_reply.py
"""

import os
import time

from agenticemail import AgenticEmail

client = AgenticEmail(
    api_key=os.environ["AGENTICEMAIL_API_KEY"],
    base_url=os.environ.get("AGENTICEMAIL_BASE_URL", "https://app.agenticemail.dev"),
)
inbox = os.environ["AGENTICEMAIL_INBOX"]
replied: set[str] = set()

print(f"Auto-reply watching {inbox} …")
while True:
    for summary in client.threads.list(inbox).get("data", []):
        thread = client.threads.get(summary["id"])
        last = thread["messages"][-1]
        if last["direction"] == "inbound" and last["id"] not in replied:
            client.messages.reply(
                inbox,
                last["id"],
                text="Thanks for your message! An agent will follow up shortly.",
            )
            replied.add(last["id"])
            print(f"Replied to {last['from']} in thread {summary['id']}")
    time.sleep(10)
