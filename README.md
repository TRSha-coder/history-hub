# 中文历史杂志资源库

这是一个可直接部署到 GitHub Pages 的静态网站，用于展示“中文历史杂志/期刊”资源索引。  
数据通过抓取脚本定时更新，前端只读取本地 JSON 文件，不依赖后端服务。

## 功能

- 中文界面，支持关键词搜索
- 按来源筛选（书格 / 中文维基百科）
- 展示资源标题、年份、摘要、跳转链接
- GitHub Actions 定时更新资源数据
- GitHub Pages 自动部署

## 项目结构

```text
.
├── index.html
├── script.js
├── styles.css
├── data/
│   └── magazines.json
├── scripts/
│   └── fetch_magazines.py
└── .github/workflows/
    ├── update-magazines.yml
    └── deploy-pages.yml
```

## 本地运行

```bash
python scripts/fetch_magazines.py
python -m http.server 8000
```

打开 `http://localhost:8000` 即可访问。

## 自动化说明

### 1) 数据更新工作流

文件：`.github/workflows/update-magazines.yml`

- 定时执行抓取脚本（每 8 小时）
- 若 `data/magazines.json` 有变化则自动提交并推送

### 2) Pages 部署工作流

文件：`.github/workflows/deploy-pages.yml`

- 分支 push 或手动触发时自动部署
- 将仓库根目录作为静态站点发布内容

## GitHub Pages 地址

- 用户主页仓库（`<username>.github.io`）：`https://<username>.github.io/`
- 项目仓库（如 `korean-news`）：`https://<username>.github.io/korean-news/`

## 说明

本项目仅聚合公开可访问资源链接，内容版权归原始站点及作者所有。
