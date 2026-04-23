---
name: ai-news-intelligence
description: >
  中美 AI/LLM 行业资讯采集与智能分析工具。覆盖 120+ 权威信源，包括公司官方博客、行业媒体、
  学术平台、Newsletter、社交媒体、政策法规、开发者社区七类渠道。支持 RSS 实时采集、
  Hacker News API 采集、web 搜索补充，由 CodeBuddy 自身完成摘要和分析。
  当用户需要了解 AI 行业最新动态、获取 AI 新闻、生成 AI 日报或周报、追踪特定 AI 公司或技术主题、
  查找最新 AI 论文时触发此 skill。
  触发词：AI 新闻、AI 资讯、AI 日报、AI 周报、LLM 动态、大模型新闻、AI 行业动态、
  今天 AI 有什么、最近 AI、追踪 AI、AI news、AI briefing、what's new in AI、
  最新 AI 论文、AI 公司动态、OpenAI 最新、Anthropic 最新、DeepSeek 最新。
  不用于一般性 AI 技术问答、代码编写或非 AI 行业的新闻查询。
---

# AI News Intelligence

中美 AI/LLM 行业资讯采集与分析工具，覆盖 120+ 权威信源。脚本负责"拿数据"，CodeBuddy 负责"理解数据"——摘要、分类、分析全部由 CodeBuddy 自身完成，无需外部 LLM API。

## 信源体系

120+ 信源按来源类型分为七类，各有各的价值，不分高低：

| 类型 | 采集方式 | RSS 可用 | 需 web_search |
|------|---------|---------|--------------|
| 公司官方 | RSS + web_search | OpenAI, DeepMind, Google AI, Meta Engineering, Microsoft AI, NVIDIA, HuggingFace | Anthropic, Mistral, DeepSeek, Qwen 等中国公司 |
| 行业媒体 | RSS + web_search | The Verge, TechCrunch, Ars Technica, MIT Tech Review, VentureBeat, 量子位 | 机器之心, 36氪, 新智元, 虎嗅 |
| 学术平台 | RSS + web_search | arXiv cs.AI, arXiv cs.CL, arXiv cs.LG | HF Daily Papers, Papers With Code |
| Newsletter | web_search | — | TLDR AI, The Batch, Import AI, Ben's Bites |
| 社交媒体 | web_search | — | @karpathy, @_akhaliq, r/LocalLLaMA, 微信公众号 |
| 政策法规 | web_search | — | NIST AI, Stanford HAI, 中国信通院 |
| 开发者社区 | HN 脚本 + web_search | Hacker News (API) | GitHub Trending, Product Hunt |

**重要**：执行 `--list-websearch` 可以获取所有需要 web_search 的源及其推荐搜索关键词。

完整的信源注册表在 `references/sources_registry.md`。

## 首次使用

安装 Python 依赖（唯一外部依赖）：

```bash
pip install feedparser
```

## 工作流决策树

收到用户请求后，按以下逻辑选择执行路径：

```
用户请求
├─ 包含"日报"/"周报"/"整理"/"汇总"
│   → 全源采集模式：执行 RSS 脚本(--all) + HN 脚本 + web_search 补充
│   → 对结果做分类摘要，按来源类型分组输出
│
├─ 包含具体公司名（如 "OpenAI", "Anthropic", "DeepSeek"）
│   → 定向采集模式：查 references/sources_registry.md 找到对应源
│   → 如有 RSS，执行 fetch_rss.py --source <id>
│   → 如无 RSS，使用 web_search 搜索 "<公司名> AI latest news"
│
├─ 包含具体主题（如 "AI Agent", "多模态", "LLM"）
│   → 主题搜索模式：执行 RSS 脚本采集 + web_search "<主题> AI latest"
│   → 从结果中筛选与主题相关的内容
│
├─ 包含"论文"/"paper"/"arXiv"/"学术"
│   → 学术模式：执行 fetch_rss.py --type academic
│   → 补充 web_search "arXiv <主题> latest papers"
│
├─ 包含"政策"/"法规"/"监管"
│   → 政策模式：web_search 搜索政策来源（参见 references/sources_registry.md 政策法规部分）
│
└─ 通用 AI 新闻请求
    → 执行 fetch_rss.py --type official,media --limit 10 --since 24h
    → 补充 HN 脚本
    → 输出结构化结果
```

## 脚本使用说明

### fetch_rss.py — RSS 采集

```bash
# 采集所有 RSS 源，最近 24 小时
python3 scripts/fetch_rss.py --all --since 24h --limit 10

# 按来源类型采集
python3 scripts/fetch_rss.py --type official --since 24h
python3 scripts/fetch_rss.py --type media --since 7d
python3 scripts/fetch_rss.py --type academic --since 24h

# 按具体来源 ID 采集
python3 scripts/fetch_rss.py --source openai-blog,anthropic-news

# 组合使用
python3 scripts/fetch_rss.py --type official,media --limit 5 --since 48h
```

参数说明：
- `--type`：来源类型，可选 official, media, academic, developer，逗号分隔多选
- `--source`：具体来源 ID，逗号分隔多选（ID 列表见 references/sources_registry.md）
- `--limit`：每个源最多返回条数（默认 10）
- `--since`：时间范围，支持 1h, 6h, 12h, 24h, 48h, 7d, 30d（默认 24h）
- `--all`：采集所有 RSS 源

输出格式为 stdout JSON 数组，每个元素包含 title, url, source_name, source_type, published_at, content_snippet 字段。

### fetch_hackernews.py — Hacker News 采集

```bash
# 默认模式：从 HN 首页过滤 AI 相关热帖（推荐）
python3 scripts/fetch_hackernews.py

# 搜索模式：按关键词搜索
python3 scripts/fetch_hackernews.py --mode search --query "LLM OR transformer" --limit 20
```

默认 front_page 模式会获取 HN 当前首页热帖并自动过滤 AI 相关内容，结果质量和时效性最好。
如果首页没有 AI 话题，会自动降级到关键词搜索。

### web_search 补充采集

对于没有 RSS 的来源（Newsletter、社交媒体、政策法规），使用 CodeBuddy 内置的 web_search 工具。
推荐搜索关键词见 references/sources_registry.md 中各来源的"搜索关键词"列。

## 摘要与分析指令

脚本返回原始数据后，由 CodeBuddy 自身完成以下处理（不调用外部 API）：

1. **一句话概括**：为每篇文章生成 20-50 字的中文摘要
2. **关键要点**：提取 2-4 个核心事实或数据点
3. **主题分类**：从以下标签中选择 1-3 个：LLM, 多模态, AI Agent, 计算机视觉, 语音AI, 机器人, AI基础设施, AI安全, 产品发布, 融资并购, 公司战略, 行业报告, 开源项目, 政策法规, 教程工具
4. **来源标注**：标明来自哪类渠道和具体来源名称

## 输出格式模板

### 日报格式

```
# AI 资讯日报 — [YYYY-MM-DD]

## 公司官方动态
1. **[标题]** — [来源名] | [时间]
   > [一句话摘要]
   - [要点1]
   - [要点2]

## 行业媒体报道
...

## 学术前沿
...

## 开发者社区
...

---
本日采集 [X] 个来源，获取 [Y] 条资讯。
```

### 快讯格式（简洁列表）

```
## AI 快讯 — [日期/时间范围]

1. **[标题]** — [来源名] | [主题标签]
   > [一句话摘要]

2. ...
```

### 主题追踪格式

```
## [主题名] 最新进展 — [时间范围]

### 概述
[CodeBuddy 对本主题近期发展的 2-3 句话总结]

### 详细内容
1. **[标题]** — [来源名] | [时间]
   > [摘要 + 关键要点]

2. ...
```
