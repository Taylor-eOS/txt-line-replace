import os
from urllib.parse import urlparse, unquote

ROLES = {"User:": "user", "Assistant:": "assistant"}

def next_nonblank(lines, i):
    i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i

def is_separator(lines, i):
    if lines[i].strip() != "---":
        return False
    j = next_nonblank(lines, i)
    return j < len(lines) and lines[j].strip() in ROLES

def parse(text):
    lines = text.split("\n")
    messages = []
    role = None
    buffer = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        separator = is_separator(lines, i)
        if separator or (role is None and stripped in ROLES):
            if role is not None:
                messages.append((role, "\n".join(buffer).strip()))
            j = next_nonblank(lines, i) if separator else i
            role = ROLES[lines[j].strip()]
            buffer = []
            i = j + 1
            continue
        if role is not None:
            buffer.append(lines[i])
        i += 1
    if role is not None:
        messages.append((role, "\n".join(buffer).strip()))
    return messages

def serialize(messages):
    blocks = [f"<{role}>\n{text}\n</{role}>" for role, text in messages]
    return "\n\n".join(blocks) + "\n"

def resolve_path(entry):
    entry = entry.strip().strip("'\"").strip()
    if entry.lower().startswith("file:"):
        return unquote(urlparse(entry).path)
    return entry

def output_path(source_path):
    folder = os.path.dirname(os.path.abspath(source_path))
    name, extension = os.path.splitext(os.path.basename(source_path))
    return os.path.join(folder, f"{name}_tagged{extension}")

def main():
    source_path = resolve_path(input("File: "))
    with open(source_path, encoding="utf-8") as f:
        text = f.read()
    messages = parse(text)
    if not messages:
        print("No messages found.")
        return
    target_path = output_path(source_path)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(serialize(messages))
    print(f"{len(messages)} messages written to {target_path}")

main()
