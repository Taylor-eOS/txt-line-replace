import os
import tempfile
from pathlib import Path

FOLDER = ""
RECURSIVE = False
DRY_RUN = False

def get_folder():
    folder = FOLDER or input("Folder path: ").strip()
    path = Path(folder).expanduser()
    if not path.is_dir():
        raise SystemExit(f"Not a folder: {path}")
    return path

def find_files(folder):
    candidates = folder.rglob("*") if RECURSIVE else folder.glob("*")
    return sorted(p for p in candidates if p.is_file() and p.suffix.lower() == ".txt")

def is_blank(line):
    return line.strip() == ""

def is_rule(line):
    return line.strip() == "---"

def fix_text(text):
    lines = text.split("\n")
    last = len(lines) - 1
    result = []
    count = 0
    i = 0
    while i <= last:
        line = lines[i]
        result.append(line)
        if is_rule(line) and i > 0 and is_blank(lines[i - 1]) and i + 1 < last and is_blank(lines[i + 1]):
            count += 1
            i += 2
        else:
            i += 1
    return "\n".join(result), count

def write_atomic(path, text):
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as tmp:
            tmp.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise

def process_file(path):
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
    except UnicodeDecodeError:
        print(f"Skipped (not UTF-8): {path}")
        return 0
    fixed, count = fix_text(text)
    if count == 0:
        return 0
    if not DRY_RUN:
        write_atomic(path, fixed)
    print(f"{'Would fix' if DRY_RUN else 'Fixed'} {count} in {path}")
    return count

def main():
    folder = get_folder()
    files = find_files(folder)
    total = 0
    changed_files = 0
    for path in files:
        count = process_file(path)
        total += count
        changed_files += 1 if count else 0
    print(f"Checked {len(files)} files, {total} separators in {changed_files} files")

if __name__ == "__main__":
    main()
