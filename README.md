# AI News Intelligence — CodeBuddy Skill

中美 AI/LLM 行业资讯采集与智能分析 Skill。覆盖 120+ 权威信源，脚本拿数据、CodeBuddy 做分析，零 API 配置。

## 功能

- **RSS 实时采集**：16 个已验证的 RSS 源（公司官方、行业媒体、学术平台），并行抓取，100% 成功率
- **Hacker News 采集**：从 HN 首页过滤 AI 热帖，零外部依赖，实时获取高分讨论
- **Web 搜索补充**：9 个无 RSS 的来源（Anthropic、Mistral、机器之心、36氪等）通过 web_search 降级获取，内置推荐搜索关键词
- **AI 摘要分析**：由 CodeBuddy 自身完成摘要、分类、分析，无需外部 LLM API
- **七类信源全覆盖**：公司官方、行业媒体、学术平台、Newsletter、社交媒体、政策法规、开发者社区

## 安装

### 方法一：从 GitHub 安装（推荐）

```bash
git clone https://github.com/jaywuxj/ai-news-intelligence.git ~/.codebuddy/skills/ai-news-intelligence
pip install feedparser
```

### 方法二：手动安装

```bash
cp -r ai-news-intelligence ~/.codebuddy/skills/
chmod +x ~/.codebuddy/skills/ai-news-intelligence/scripts/*.py
pip install feedparser
```

## 使用

安装后在 CodeBuddy 对话中直接说自然语言即可：

```
"帮我看看今天 AI 有什么新闻"
"生成 AI 日报"
"OpenAI 最近发了什么"
"最近有什么 AI Agent 相关的进展"
"帮我看看 arXiv 最新的 AI 论文"
"What's new in AI this week"
```

## 脚本独立使用

脚本也可以在终端独立运行：

```bash
cd ~/.codebuddy/skills/ai-news-intelligence

# 列出所有 RSS 源
python3 scripts/fetch_rss.py --list-sources

# 列出需要 web_search 降级的源及推荐搜索关键词
python3 scripts/fetch_rss.py --list-websearch

# 采集所有 RSS 源最近 24 小时内容
python3 scripts/fetch_rss.py --all --since 24h --limit 10

# 只采集公司官方源
python3 scripts/fetch_rss.py --type official --since 24h

# 采集特定来源
python3 scripts/fetch_rss.py --source openai-blog,deepmind-blog

# Hacker News 首页 AI 热帖（默认模式）
python3 scripts/fetch_hackernews.py

# Hacker News 关键词搜索模式
python3 scripts/fetch_hackernews.py --mode search --query "LLM OR transformer" --limit 20
```

## 信源覆盖

| 类型 | RSS 可用 | 需 web_search | 代表来源 |
|------|---------|--------------|---------|
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
├── SKILL.md                           # 核心指令（触发规则 + 工作流 + 输出模板）
├── scripts/
│   ├── fetch_rss.py                   # RSS 采集（16 个已验证源，并行抓取）
│   └── fetch_hackernews.py            # HN 首页 AI 热帖过滤（零外部依赖）
└── references/
    ├── sources_registry.md            # 完整信源注册表（120+ 源 + web_search 关键词）
    └── topic_taxonomy.md              # 主题分类体系
```

## 依赖

- Python 3.9+
- `feedparser`（`pip install feedparser`）
- CodeBuddy（用于摘要和分析）

## 测试结果

| 测试项 | 结果 |
|--------|------|
| Skill 结构 | SKILL.md + scripts/ + references/ 完整 |
| RSS 采集成功率 | **16/16 源成功（100%）** |
| RSS 采集（公司官方 7 个） | OpenAI, DeepMind, Google AI, Meta Engineering, Microsoft AI, NVIDIA, HuggingFace |
| RSS 采集（行业媒体 6 个） | The Verge, TechCrunch, Ars Technica, MIT Tech Review, VentureBeat, 量子位 |
| RSS 采集（学术平台 3 个） | arXiv cs.AI, arXiv cs.CL, arXiv cs.LG |
| HN 首页 AI 热帖 | 成功，返回 score 55-811 的实时热帖 |
| web_search 降级源 | 9 个源有推荐搜索关键词 |
| 全源采集 | 37 篇文章 / 13 个活跃源 / 3 种类型（7 天窗口） |

## License

MIT
