# AI News Intelligence

中美 AI/LLM 行业资讯采集与智能分析工具。覆盖 120+ 权威信源，脚本负责采集数据，可搭配任意 AI 编程助手或独立使用。

## 功能

- **RSS 实时采集**：16 个已验证的 RSS 源（公司官方、行业媒体、学术平台），并行抓取，100% 成功率
- **Hacker News 采集**：从 HN 首页过滤 AI 热帖，零外部依赖，实时获取高分讨论
- **Web 搜索补充**：9 个无 RSS 的来源（Anthropic、Mistral、机器之心、36氪等）提供推荐搜索关键词，可配合搜索引擎或 AI 助手获取
- **AI 摘要分析**：采集结果可直接交给任意 LLM（ChatGPT、Claude、Kimi 等）做摘要和分析，无需额外 API 配置
- **七类信源全覆盖**：公司官方、行业媒体、学术平台、Newsletter、社交媒体、政策法规、开发者社区

## 安装

```bash
git clone https://github.com/jaywuxj/ai-news-intelligence.git
cd ai-news-intelligence
pip install feedparser
```

如果作为 AI 编程助手的 Skill 使用，将目录放到对应的 skills 路径下即可（如 `~/.codebuddy/skills/`、`~/.claude/skills/` 等）。

## 使用

### 命令行独立使用

```bash
# 列出所有 RSS 源
python3 scripts/fetch_rss.py --list-sources

# 列出需要搜索引擎补充的源及推荐关键词
python3 scripts/fetch_rss.py --list-websearch

# 采集所有 RSS 源最近 24 小时内容
python3 scripts/fetch_rss.py --all --since 24h --limit 10

# 只采集公司官方源
python3 scripts/fetch_rss.py --type official --since 24h

# 只采集学术平台
python3 scripts/fetch_rss.py --type academic --since 7d

# 采集特定来源
python3 scripts/fetch_rss.py --source openai-blog,deepmind-blog

# Hacker News 首页 AI 热帖（默认模式）
python3 scripts/fetch_hackernews.py

# Hacker News 关键词搜索模式
python3 scripts/fetch_hackernews.py --mode search --query "LLM OR transformer" --limit 20
```

脚本输出 JSON 到 stdout，可管道传给其他工具或 LLM 处理：

```bash
# 采集后用 jq 提取标题
python3 scripts/fetch_rss.py --type official --since 24h 2>/dev/null | jq '.[].title'

# 采集后存文件，再交给 AI 做摘要
python3 scripts/fetch_rss.py --all --since 24h 2>/dev/null > today_news.json
```

### 作为 AI 助手 Skill 使用

安装到对应 skills 目录后，在对话中直接说自然语言即可：

```
"帮我看看今天 AI 有什么新闻"
"生成 AI 日报"
"OpenAI 最近发了什么"
"最近有什么 AI Agent 相关的进展"
"帮我看看 arXiv 最新的 AI 论文"
"What's new in AI this week"
```

`SKILL.md` 包含完整的触发规则、工作流决策树和输出模板，兼容支持 Skill 机制的 AI 编程助手。

## 信源覆盖

| 类型 | RSS 可用 | 需搜索补充 | 代表来源 |
|------|---------|-----------|---------|
| 公司官方 | 7 个 | 5 个 | OpenAI, DeepMind, Google AI, Meta, Microsoft, NVIDIA, HuggingFace / Anthropic, Mistral, DeepSeek, Qwen |
| 行业媒体 | 6 个 | 3 个 | The Verge, TechCrunch, Ars Technica, MIT Tech Review, VentureBeat, 量子位 / 机器之心, 36氪, 新智元 |
| 学术平台 | 3 个 | 2 个 | arXiv cs.AI, arXiv cs.CL, arXiv cs.LG / HF Daily Papers, Papers With Code |
| Newsletter | — | 7+ | TLDR AI, The Batch, Import AI, Ben's Bites |
| 社交媒体 | — | 15+ | @karpathy, @_akhaliq, r/LocalLLaMA, 微信公众号 |
| 政策法规 | — | 10+ | NIST AI, Stanford HAI, 中国信通院 |
| 开发者社区 | HN API | 3+ | Hacker News, GitHub Trending, Product Hunt |

## 文件结构

```
ai-news-intelligence/
├── SKILL.md                           # AI 助手指令（触发规则 + 工作流 + 输出模板）
├── scripts/
│   ├── fetch_rss.py                   # RSS 采集（16 个已验证源，并行抓取）
│   └── fetch_hackernews.py            # HN 首页 AI 热帖过滤（零外部依赖）
└── references/
    ├── sources_registry.md            # 完整信源注册表（120+ 源 + 搜索关键词）
    └── topic_taxonomy.md              # 主题分类体系
```

## 依赖

- Python 3.9+
- `feedparser`（`pip install feedparser`）
- 可选：任意 AI 助手（用于摘要和分析）

## 测试结果

| 测试项 | 结果 |
|--------|------|
| RSS 采集成功率 | **16/16 源成功（100%）** |
| RSS — 公司官方（7 个） | OpenAI, DeepMind, Google AI, Meta Engineering, Microsoft AI, NVIDIA, HuggingFace |
| RSS — 行业媒体（6 个） | The Verge, TechCrunch, Ars Technica, MIT Tech Review, VentureBeat, 量子位 |
| RSS — 学术平台（3 个） | arXiv cs.AI, arXiv cs.CL, arXiv cs.LG |
| HN 首页 AI 热帖 | 成功，返回 score 55-811 的实时热帖 |
| 搜索补充源 | 9 个源有推荐搜索关键词 |
| 全源采集 | 37 篇文章 / 13 个活跃源 / 3 种类型（7 天窗口） |

## License

MIT
