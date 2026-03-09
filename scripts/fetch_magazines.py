import json
from pathlib import Path
import requests

URL = "https://gutendex.com/books/"
OUT = Path(__file__).resolve().parents[1] / "data" / "magazines.json"

def fetch_rows(limit: int = 100) -> list[dict]:
    # 使用 Gutendex API 搜索 history 相关的书籍
    params = {
        "topic": "history",
    }
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    
    items = []
    for d in results[:limit]:
        ident = str(d.get("id"))
        title = d.get("title", "Unknown")
        
        authors = [a.get("name") for a in d.get("authors", []) if a.get("name")]
        subjects = d.get("subjects", [])
        
        description = ""
        if authors:
            description = f"Author(s): {', '.join(authors)}"
            
        # Gutenberg 书籍链接，支持站内阅读 iframe
        read_url = f"https://www.gutenberg.org/ebooks/{ident}"
        
        # 如果有 html 格式，可以直接提供给站内阅读器更好的体验，但这里默认用书籍落地页
        formats = d.get("formats", {})
        html_url = formats.get("text/html") or formats.get("text/html; charset=utf-8")
        if html_url:
            read_url = html_url
            
        items.append({
            "identifier": ident,
            "title": title,
            "year": "N/A", # 古登堡接口通常不直接提供首次出版年份
            "subject": subjects[:10],
            "description": description,
            "url": read_url
        })
        
    return items

def main() -> None:
    print("Fetching data from Project Gutenberg (Gutendex)...")
    items = fetch_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "source": "Project Gutenberg",
                "query": "topic: history",
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
