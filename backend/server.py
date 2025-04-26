import os
import requests
import json
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-large-latest"

SYSTEM_PROMPT = (
    "You are a coding assistant. When given a prompt, generate the requested code and provide a brief explanation. "
    "Always put the code inside a <code>...</code> tag, and the explanation outside the tag. "
    "For example:\n"
    "<code>\n# code here\n</code>\nExplanation: ...\n"
    "Respond in markdown format if possible."
)

def stream_mistral_response(user_prompt, history=None):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    # Build messages with history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for turn in history[-10:]:
            messages.append({"role": "user", "content": turn["prompt"]})
            messages.append({"role": "assistant", "content": turn["response"]})
    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": MISTRAL_MODEL,
        "messages": messages,
        "stream": True
    }
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        json=data,
        headers=headers,
        stream=True
    )
    def generate():
        for line in response.iter_lines():
            if line:
                try:
                    chunk = line.decode("utf-8")
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]
                    obj = json.loads(chunk)
                    content = (
                        obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        or obj.get("choices", [{}])[0].get("message", {}).get("content", "")
                    )
                    if content:
                        yield content
                except Exception:
                    continue
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    history = data.get("history", [])
    return stream_mistral_response(user_prompt, history)

if __name__ == "__main__":
    app.run(debug=True)