# Web Scraper Template — Configurable + Stealth / 可配置爬虫 + 反检测

> **Who is this for?** Python developers who need a configurable, anti-detection web scraper they can deploy in 5 minutes — no crawling framework to learn.

[English](#english) | [中文](#中文)

---

## English

![Python](https://img.shields.io/badge/python-3.10+-blue) ![Playwright](https://img.shields.io/badge/playwright-1.30+-2EAD33)

### Supported Environment

| Software | Required | Tested |
|----------|----------|--------|
| Python | 3.10+ | 3.10.20 ✅ |
| Playwright | 1.30+ | ✅ |
| Pandas | 1.5+ | ✅ |

### Quick Start

```bash
pip install -r requirements.txt
playwright install chromium

python run.py --config sites/demo.yaml
```

Output appears in `output/` directory as CSV or JSON.

**→ [Open Live Preview](preview.html)** — terminal output + results in one page

### Example Output

```
[demo-jobs] Starting scrape...
  → file:///...sites/demo.html
    5 items extracted
[demo-jobs] Done. Total: 5 items
Saved 5 items → output/demo.csv
```

```csv
title,company,salary
Senior Python Developer,TechCorp Inc.,$120k - $150k
Data Engineer,DataFlow Ltd.,$100k - $130k
Full-Stack Developer,WebWorks GmbH,$90k - $120k
ML Engineer,AI Labs,$130k - $160k
DevOps Specialist,CloudFirst,$110k - $140k
```

### Project Structure

```
scraper-template/
├── scraper/
│   └── engine.py       # StealthScraper + ScraperConfig
├── sites/              # YAML config files
│   ├── demo.yaml       # Local demo (5 job listings)
│   └── hackernews.yaml # HN jobs example
├── output/             # Generated CSV/JSON results
├── run.py              # CLI entry point
├── requirements.txt
└── README.md
```

### Usage

Define a YAML config, then run:

```bash
python run.py -c sites/mytarget.yaml -o output/results.csv
```

### Anti-Detection Features

- Removes `navigator.webdriver`
- Randomized viewport and user-agent
- Random delays between requests
- `domcontentloaded` wait strategy
- Configurable selectors via YAML

---

## 中文

### 支持环境

| 软件 | 要求版本 | 实测 |
|------|---------|------|
| Python | 3.10+ | 3.10.20 ✅ |
| Playwright | 1.30+ | ✅ |
| Pandas | 1.5+ | ✅ |

### 快速启动

```bash
pip install -r requirements.txt
playwright install chromium

python run.py --config sites/demo.yaml
```

输出保存在 `output/` 目录，支持 CSV 和 JSON 格式。

### 示例输出

```
[demo-jobs] 开始采集...
  → file:///...sites/demo.html
    提取 5 条
[demo-jobs] 完成。共 5 条
已保存 5 条 → output/demo.csv
```

输出的 CSV 文件包含标题、公司、薪资等结构化字段。

### 项目结构

```
scraper-template/
├── scraper/
│   └── engine.py       # 反检测爬虫引擎
├── sites/              # YAML 站点配置
│   ├── demo.yaml       # 本地演示 (5条职位)
│   └── hackernews.yaml # HN 职位示例
├── output/             # 输出 CSV/JSON
├── run.py              # 命令行入口
├── requirements.txt
└── README.md
```

### 使用方式

编写 YAML 配置文件，指定目标 URL 和 CSS 选择器后运行：

```bash
python run.py -c sites/你的站点.yaml -o output/结果.csv
```

### 反检测特性

- 移除 `navigator.webdriver` 标记
- 随机化视口和 User-Agent
- 请求间随机延时
- `domcontentloaded` 等待策略
- YAML 配置选择器，零代码改参数

---

*Author: Ck.epsilon & Chaos (AI Programming Assistant)*
