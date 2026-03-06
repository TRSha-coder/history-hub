#!/usr/bin/env python3
"""抓取中文历史杂志资源并生成静态 JSON。"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

OUTPUT_PATH = Path("data/magazines.json")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

YEAR_RE = re.compile(r"(1[6-9]\d{2}|20\d{2})")
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
SHUGE_ENTRY_RE = re.compile(
    r"<article class='main_color inner-entry'.*?</article>",
    re.S,
)
SHUGE_LINK_RE = re.compile(r"<a href='(https://www\.shuge\.org/view/[^']+/)' title='([^']+)'")
SHUGE_SUMMARY_RE = re.compile(r"grid-entry-excerpt entry-content'[^>]*>(.*?)</div>", re.S)


def fetch_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def fetch_text(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "；".join(str(v) for v in value if v is not None)
    return str(value).strip()


def clean_html_text(value: str) -> str:
    value = TAG_RE.sub(" ", value)
    value = html.unescape(value)
    return WHITESPACE_RE.sub(" ", value).strip()


def extract_year(*candidates: Any) -> str:
    for value in candidates:
        text = normalize_text(value)
        if not text:
            continue
        exact = re.search(r"(1[6-9]\d{2}|20\d{2})\s*年", text)
        if exact:
            return exact.group(1)
        ranged = re.search(
            r"(1[6-9]\d{2}|20\d{2})\s*[至到\-~]\s*(1[6-9]\d{2}|20\d{2})\s*年?",
            text,
        )
        if ranged:
            return ranged.group(1)
        for matched in YEAR_RE.finditer(text):
            # 过滤“1767幅”这类数量，避免把数量误识别成年份
            suffix = text[matched.end() : matched.end() + 2].strip()
            if suffix[:1] in {"幅", "页", "张", "个", "期", "卷"}:
                continue
            return matched.group(1)
    return ""


def batch(seq: list[str], size: int) -> list[list[str]]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


def fetch_shuge(max_items: int = 70) -> list[dict[str, Any]]:
    keywords = ("杂志", "期刊", "画报")
    query_terms = ("杂志", "期刊", "民国 杂志", "画报")
    results: list[dict[str, Any]] = []

    for term in query_terms:
        html_text = fetch_text(f"https://www.shuge.org/?s={quote(term)}")
        entries = SHUGE_ENTRY_RE.findall(html_text)
        for entry in entries:
            link_match = SHUGE_LINK_RE.search(entry)
            if not link_match:
                continue
            link, title = link_match.group(1), clean_html_text(link_match.group(2))
            summary_match = SHUGE_SUMMARY_RE.search(entry)
            summary = clean_html_text(summary_match.group(1)) if summary_match else ""
            search_blob = f"{title} {summary}"
            if not any(k in search_blob for k in keywords):
                continue
            year = extract_year(title, summary)
            results.append(
                {
                    "id": f"shuge-{link.rsplit('/', 2)[-2]}",
                    "title": title,
                    "summary": (summary[:180] + "...") if len(summary) > 180 else summary,
                    "year": year,
                    "date": "",
                    "source": "shuge",
                    "subjects": "书格, 历史文献, 杂志",
                    "link": link,
                }
            )
            if len(results) >= max_items:
                return results
    return results


def fetch_zh_wikipedia(max_items: int = 90) -> list[dict[str, Any]]:
    endpoint = "https://zh.wikipedia.org/w/api.php"
    categories = (
        "Category:中国已停刊杂志",
        "Category:上海民国时期已停刊杂志",
        "Category:清朝杂志",
        "Category:香港已停刊杂志",
        "Category:臺灣已停刊雜誌",
    )
    titles: list[str] = []

    for category in categories:
        cmcontinue = None
        for _ in range(5):
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                "cmnamespace": 0,
                "cmlimit": 200,
                "format": "json",
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue
            payload = fetch_json(f"{endpoint}?{urlencode(params)}")
            for member in payload.get("query", {}).get("categorymembers", []):
                title = normalize_text(member.get("title"))
                if title:
                    titles.append(title)
            cmcontinue = payload.get("continue", {}).get("cmcontinue")
            if not cmcontinue:
                break

    # 去重，后续分批拉取摘要
    unique_titles = []
    seen = set()
    for title in titles:
        if title in seen:
            continue
        seen.add(title)
        unique_titles.append(title)
        if len(unique_titles) >= max_items:
            break

    items: list[dict[str, Any]] = []
    for title_batch in batch(unique_titles, 20):
        params = {
            "action": "query",
            "prop": "extracts|info",
            "inprop": "url",
            "exintro": 1,
            "explaintext": 1,
            "titles": "|".join(title_batch),
            "format": "json",
        }
        payload = fetch_json(f"{endpoint}?{urlencode(params)}")
        pages = payload.get("query", {}).get("pages", {})
        for page in pages.values():
            title = normalize_text(page.get("title"))
            if not title:
                continue
            extract = normalize_text(page.get("extract"))
            year = extract_year(title, extract)
            items.append(
                {
                    "id": f"zhwiki-{page.get('pageid', title)}",
                    "title": title,
                    "summary": (extract[:180] + "...") if len(extract) > 180 else extract,
                    "year": year,
                    "date": "",
                    "source": "zh-wikipedia",
                    "subjects": "中文维基百科, 杂志词条",
                    "link": normalize_text(page.get("fullurl")),
                }
            )
    return items


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = normalize_text(item.get("link")) or normalize_text(item.get("title"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key_fn(item: dict[str, Any]) -> tuple[int, str]:
        year = normalize_text(item.get("year"))
        try:
            score = int(year)
        except ValueError:
            score = 9999
        return (score, normalize_text(item.get("title")))

    return sorted(items, key=key_fn)


def now_cst() -> str:
    cst = dt.timezone(dt.timedelta(hours=8))
    return dt.datetime.now(dt.timezone.utc).astimezone(cst).strftime("%Y-%m-%d %H:%M:%S UTC+8")


def build_payload(items: list[dict[str, Any]]) -> dict[str, Any]:
    source_stats: dict[str, int] = {}
    for item in items:
        source = normalize_text(item.get("source")) or "unknown"
        source_stats[source] = source_stats.get(source, 0) + 1
    return {
        "status": "ok",
        "meta": {
            "updatedAt": now_cst(),
            "total": len(items),
            "sourceStats": source_stats,
        },
        "items": items,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_items: list[dict[str, Any]] = []
    for source_name, fn in (
        ("shuge", fetch_shuge),
        ("zh-wikipedia", fetch_zh_wikipedia),
    ):
        try:
            source_items = fn()
            all_items.extend(source_items)
            print(f"[ok] {source_name}: {len(source_items)} 条")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] {source_name} 抓取失败: {exc}")

    deduped = sort_items(dedupe_items(all_items))
    payload = build_payload(deduped)

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] 已写入 {OUTPUT_PATH}，共 {len(deduped)} 条")


if __name__ == "__main__":
    main()
