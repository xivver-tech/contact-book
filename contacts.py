#!/usr/bin/env python3
"""
Local Contact Book
- Add / search / list / edit / delete contacts
- Tags + notes
- Export to CSV or vCard-ish text
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent / "contacts.json"

def load():
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def next_id(data):
    return max([c.get("id", 0) for c in data] + [0]) + 1

def add():
    data = load()
    name = input("Name: ").strip()
    if not name:
        print("Name required.")
        return
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    tags = [t.strip().lower() for t in input("Tags (comma separated): ").split(",") if t.strip()]
    notes = input("Notes: ").strip()

    contact = {
        "id": next_id(data),
        "name": name,
        "email": email,
        "phone": phone,
        "tags": tags,
        "notes": notes,
        "created": datetime.now().isoformat(timespec="seconds")
    }
    data.append(contact)
    save(data)
    print(f"✓ Added #{contact['id']}: {name}")

def list_all(tag=None):
    data = load()
    if tag:
        data = [c for c in data if tag.lower() in c.get("tags", [])]
    if not data:
        print("No contacts.")
        return
    for c in sorted(data, key=lambda x: x["name"].lower()):
        tags = ", ".join(c.get("tags", [])) or "-"
        print(f"#{c['id']:<4} {c['name']:<25} {c.get('email','') or '-':<30} {tags}")

def search(query):
    data = load()
    q = query.lower()
    results = []
    for c in data:
        hay = " ".join([
            c.get("name", ""),
            c.get("email", ""),
            c.get("phone", ""),
            c.get("notes", ""),
            " ".join(c.get("tags", []))
        ]).lower()
        if q in hay:
            results.append(c)
    if not results:
        print("No matches.")
        return
    for c in results:
        print(f"#{c['id']}  {c['name']}")
        if c.get("email"): print(f"     email: {c['email']}")
        if c.get("phone"): print(f"     phone: {c['phone']}")
        if c.get("tags"): print(f"     tags: {', '.join(c['tags'])}")
        if c.get("notes"): print(f"     notes: {c['notes']}")
        print()

def delete(cid):
    data = load()
    new = [c for c in data if c["id"] != cid]
    if len(new) == len(data):
        print("ID not found.")
        return
    save(new)
    print(f"✓ Deleted #{cid}")

def export_csv(path="contacts.csv"):
    data = load()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "phone", "tags", "notes"])
        writer.writeheader()
        for c in data:
            writer.writerow({
                "id": c["id"],
                "name": c["name"],
                "email": c.get("email", ""),
                "phone": c.get("phone", ""),
                "tags": "|".join(c.get("tags", [])),
                "notes": c.get("notes", "")
            })
    print(f"✓ Exported {len(data)} contacts to {path}")

def main():
    if len(sys.argv) < 2:
        print("""Contact Book
============
  add              Add a contact
  list [--tag x]   List contacts
  search <query>   Full-text search
  delete <id>      Delete contact
  export [file]    Export to CSV
""")
        return

    cmd = sys.argv[1].lower()
    if cmd == "add":
        add()
    elif cmd == "list":
        tag = None
        if "--tag" in sys.argv:
            idx = sys.argv.index("--tag")
            if idx + 1 < len(sys.argv):
                tag = sys.argv[idx + 1]
        list_all(tag)
    elif cmd == "search" and len(sys.argv) > 2:
        search(" ".join(sys.argv[2:]))
    elif cmd == "delete" and len(sys.argv) > 2:
        try:
            delete(int(sys.argv[2]))
        except ValueError:
            print("ID must be a number")
    elif cmd == "export":
        path = sys.argv[2] if len(sys.argv) > 2 else "contacts.csv"
        export_csv(path)
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
