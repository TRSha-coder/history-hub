import json
from pathlib import Path
import requests

URL = "https://openlibrary.org/search.json"
OUT = Path(__file__).resolve().parents[1] / "data" / "magazines.json"

def fetch_rows(limit: int = 100) -> list[dict]:
    params = {
        "q": "history magazine",
        "limit": limit,
        "fields": "key,title,first_publish_year,author_name,subject"
    }
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    docs = r.json().get("docs", [])
    
    items = []
    for d in docs:
        key = d.get("key", "").replace("/works/", "")
        if not key:
            continue
        
        subjects = d.get("subject", [])
        authors = d.get("author_name", [])
        
        description = ""
        if authors:
            description = f"Author(s): {', '.join(authors)}"
            
        items.append({
            "identifier": key,
            "title": d.get("title", "Unknown"),
            "year": str(d.get("first_publish_year", "")),
            "subject": subjects[:10],
            "description": description,
            "url": f"https://openlibrary.org/works/{key}"
        })
        
    return items

def main() -> None:
    print("Fetching data from Open Library...")
    items = fetch_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "source": "Open Library",
                "query": "q: history magazine",
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"done: {len(items)} -> {OUT}")

if __name__ == "__main__":
    main()
