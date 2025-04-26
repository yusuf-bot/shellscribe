import argparse
import requests
import sys
import re
import os
import json

SERVER_URL = "https://shellscribe.onrender.com/generate"
HISTORY_FILE = os.path.expanduser("~/.shellscribe_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)

def add_to_history(history, prompt, response):
    history.append({"prompt": prompt, "response": response})
    return history[-10:]

def stream_response(prompt):
    history = load_history()
    payload = {
        "prompt": prompt,
        "history": history[-10:]
    }
    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            stream=True
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            sys.exit(1)

        code_buffer = ['<code>']
        explanation_buffer = []
        in_code = False
        full_response = ""

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            full_response += line
            if "<code>" in line:
                in_code = True
                line = line.split("<code>", 1)[1]
            if "</code>" in line:
                code_part, rest = line.split("</code>", 1)
                code_buffer.append(code_part)
                code_buffer.append("</code>")
                in_code = False
                if rest:
                    explanation_buffer.append(rest)
                continue
            if in_code:
                code_buffer.append(line)
            else:
                explanation_buffer.append(line)

        code = code_buffer
        if code:
            for code_line in code:
                code_line = code_line.strip("\n")
                if code_line.startswith("```python"):
                    code_line = code_line[9:]
                if code_line.endswith("```"):
                    code_line = code_line[:-3]
                if code_line:
                    print(code_line)
        explanation = "".join(explanation_buffer).strip()
        if explanation:
            print(explanation)
        # Save to history
        history = add_to_history(history, prompt, full_response)
        save_history(history)
    except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError):
        pass

def extract_code_from_stream(prompt, file_path, mode="w"):
    history = load_history()
    payload = {
        "prompt": prompt,
        "history": history[-10:]
    }
    response = requests.post(
        SERVER_URL,
        json=payload,
        stream=True
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)
    full_response = ""
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            print(chunk, end="", flush=True)
            full_response += chunk
    code = ""
    start = full_response.find("<code>")
    end = full_response.find("</code>")
    if start != -1 and end != -1 and end > start:
        code = full_response[start + len("<code>"):end]
        code = code.replace("```python", "").replace("```", "").lstrip("\n")
    with open(file_path, mode, encoding="utf-8") as f:
        f.write(code)
    print(f"\nCode written to {file_path}")
    # Save to history
    history = add_to_history(history, prompt, full_response)
    save_history(history)

def main():
    parser = argparse.ArgumentParser(description="Shellscribe CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)

    write_parser = subparsers.add_parser('write', help='Generate code and output to terminal')
    write_parser.add_argument('prompt', help='Prompt for code generation')

    file_parser = subparsers.add_parser('file', help='Generate code and write to a file')
    file_parser.add_argument('prompt', help='Prompt for code generation')
    file_parser.add_argument('filepath', help='File to write code to')
    file_parser.add_argument('--append', action='store_true', help='Append to file instead of overwrite')

    args = parser.parse_args()

    if args.command == 'write':
        stream_response(args.prompt)
        print()
    elif args.command == 'file':
        mode = "a" if args.append else "w"
        extract_code_from_stream(args.prompt, args.filepath, mode)

if __name__ == "__main__":
    main()