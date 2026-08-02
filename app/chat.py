#!/usr/bin/env python3
# Terminal chat client for AgriPadi. Talks to a local llama-server instance.

import json
import sys
import urllib.request

SERVER_URL = "http://127.0.0.1:8090/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are AgriPadi, an offline farming advisor for smallholder farmers and "
    "agricultural extension officers in Nigeria and West Africa. Give practical, "
    "specific advice on crops, livestock, and market decisions. Keep answers "
    "concise and actionable. If you are not sure, say so rather than guessing."
)


def stream_reply(messages):
    payload = json.dumps(
        {
            "model": "agripadi",
            "messages": messages,
            "temperature": 0.3,
            "stream": True,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        SERVER_URL, data=payload, headers={"Content-Type": "application/json"}
    )

    reply = ""
    with urllib.request.urlopen(req) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data: "):
                continue
            data = line[len("data: "):]
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            delta = chunk["choices"][0]["delta"].get("content", "")
            if delta:
                print(delta, end="", flush=True)
                reply += delta
    print()
    return reply


def main():
    print("AgriPadi — offline farming advisor (type 'exit' to quit)\n")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        print("AgriPadi: ", end="", flush=True)
        try:
            reply = stream_reply(messages)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[error contacting local model server: {exc}]")
            print("Is llama-server running? See app/run.sh.")
            sys.exit(1)
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
