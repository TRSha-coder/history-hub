import json
from pathlib import Path

OUT_JSON = Path(__file__).resolve().parents[1] / "data" / "magazines.json"
OUT_BOOKS_DIR = Path(__file__).resolve().parents[1] / "data" / "books"

# 模拟一些国内友好的历史资料数据（古典历史文献、历史期刊示例等）
MOCK_DATA = [
    {
        "identifier": "shiji-01",
        "title": "史记 · 五帝本纪",
        "year": "西汉",
        "author": "司马迁",
        "subject": ["中国历史", "纪传体通史", "上古史"],
        "description": "《史记》是中国历史上第一部纪传体通史，被列为“二十四史”之首。本篇为《五帝本纪》，记载了黄帝、颛顼、帝喾、尧、舜的生平事迹。",
        "content": "<h1>史记 · 五帝本纪</h1><p>黄帝者，少典之子，姓公孙，名曰轩辕。生而神灵，弱而能言，幼而徇齐，长而敦敏，成而聪明...</p><p>（此处为测试使用的本地模拟正文，加载速度极快，且完全支持沉浸式翻译插件的网页翻译功能。）</p><p>由于是本地相对路径加载，不存在跨域问题和网络延迟问题。</p>"
    },
    {
        "identifier": "zizhitongjian-01",
        "title": "资治通鉴 · 周纪一",
        "year": "北宋",
        "author": "司马光",
        "subject": ["中国历史", "编年体通史", "古代政治"],
        "description": "《资治通鉴》是由北宋史学家司马光主编的一部多卷本编年体史书。本篇起于周威烈王二十三年，终于周烈王三十三年。",
        "content": "<h1>资治通鉴 · 周纪一</h1><p>起著雍摄提格，尽玄黓困敦，凡三十五年。</p><p>威烈王二十三年（戊寅，公元前四零三年）</p><p>初命晋大夫魏斯、赵籍、韩虔为诸侯...</p><p>（测试正文内容。你可以尝试使用沉浸式翻译插件对这段文言文或者整个页面进行翻译测试。）</p>"
    },
    {
        "identifier": "history-mag-01",
        "title": "近代史研究 (示例期刊)",
        "year": "2023",
        "author": "近代史研究所",
        "subject": ["近代史", "学术期刊", "历史研究"],
        "description": "探讨中国近代史上的重大历史事件与社会变迁。本期特稿：晚清社会经济结构转型分析。",
        "content": "<h1>近代史研究 - 晚清社会经济结构转型</h1><p>摘要：本文分析了19世纪中叶至20世纪初，在西方工业文明冲击下，中国传统农业社会的自然经济解体过程...</p><p>1. 导言：传统经济的韧性与脆弱性<br>2. 开埠通商与区域市场的形成<br>3. 结论：被动卷入全球化的历史回响</p>"
    },
    {
        "identifier": "world-history-01",
        "title": "世界历史摘要：工业革命",
        "year": "2024",
        "author": "历史学苑",
        "subject": ["世界历史", "工业革命", "欧洲史"],
        "description": "简述18世纪从英国发源的第一次工业革命如何彻底改变了人类社会的生产方式和阶级结构。",
        "content": "<h1>工业革命 (The Industrial Revolution)</h1><p>工业革命（The Industrial Revolution）开始于十八世纪六十年代，通常认为它发源于英格兰中部地区，是指资本主义工业化的早期历程...</p><p>核心发明：珍妮纺纱机、瓦特改良蒸汽机。</p><p>This is a paragraph in English to test the translation plugin. The Industrial Revolution marked a major turning point in history; almost every aspect of daily life was influenced in some way.</p>"
    }
]

def main() -> None:
    print("生成本地历史文献数据...")
    OUT_BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    
    items = []
    for d in MOCK_DATA:
        ident = d["identifier"]
        
        # 将正文生成本地 HTML 文件
        html_path = OUT_BOOKS_DIR / f"{ident}.html"
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{d['title']}</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #fff; }}
  h1 {{ color: #1a1a1a; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
  p {{ margin-bottom: 1em; font-size: 16px; }}
</style>
</head>
<body>
{d['content']}
</body>
</html>
"""
        html_path.write_text(html_content, encoding="utf-8")
        
        # 记录元数据
        items.append({
            "identifier": ident,
            "title": d["title"],
            "year": d["year"],
            "subject": d["subject"],
            "description": f"作者：{d['author']}。{d['description']}",
            # 直接指向本地生成的 HTML 文件，解决跨域和加载慢的问题
            "url": f"./data/books/{ident}.html"
        })
        
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(
            {
                "source": "Local Pre-generated Content",
                "query": "本地中国历史与世界历史数据集",
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"done: {len(items)} 条数据及 HTML 已生成。")

if __name__ == "__main__":
    main()
