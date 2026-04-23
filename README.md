# AI News Intelligence — CodeBuddy Skill

中美 AI/LLM 行业资讯采集与智能分析 Skill。覆盖 120+ 权威信源，脚本拿数据、CodeBuddy 做分析，零 API 配置。

## 功能

- **RSS 实时采集**：从 21 个内置 RSS 源（公司官方、行业媒体、学术平台、开发者社区）并行抓取最新内容
- **Hacker News 采集**：零依赖 API 调用，获取 AI 相关技术讨论
- **Web 搜索补充**：Newsletter、社交媒体、政策法规等无 RSS 的来源通过 CodeBuddy 内置搜索获取
- **AI 摘要分析**：由 CodeBuddy 自身完成摘要、分类、分析，无需外部 LLM API
- **七类信源全覆盖**：公司官方、行业媒体、学术平台、Newsletter、社交媒体、政策法规、开发者社区

## 安装

### 方法一：用户级安装（推荐）

```bash
# 解压到 CodeBuddy skills 目录
unzip ai-news-intelligence.zip -d ~/.codebuddy/skills/

# 安装唯一依赖
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

# 列出所有内置 RSS 源
python3 scripts/fetch_rss.py --list-sources

# 采集所有源最近 24 小时内容
python3 scripts/fetch_rss.py --all --since 24h --limit 10

# 只采集公司官方源
python3 scripts/fetch_rss.py --type official --since 24h

# 采集特定来源
python3 scripts/fetch_rss.py --source openai-blog,anthropic-news

# Hacker News AI 热帖
python3 scripts/fetch_hackernews.py --limit 15
```

## 信源覆盖

| 类型 | 数量 | 采集方式 | 代表来源 |
|------|------|---------|---------|
| 公司官方 | 20+ | RSS + web_search | OpenAI, Anthropic, DeepMind, Meta AI, DeepSeek, Qwen |
| 行业媒体 | 15+ | RSS + web_search | The Verge, TechCrunch, 机器之心, 量子位, 36氪 |
| 学术平台 | 5+ | RSS + web_search | arXiv, HF Daily Papers, Papers With Code |
| Newsletter | 7+ | web_search | TLDR AI, The Batch, Import AI |
| 社交媒体 | 15+ | web_search | @karpathy, r/LocalLLaMA, 机器之心公众号 |
| 政策法规 | 10+ | web_search | NIST AI, Stanford HAI, 中国信通院 |
| 开发者社区 | 5+ | HN 脚本 + web_search | Hacker News, GitHub Trending |

## 文件结构

```
ai-news-intelligence/
├── SKILL.md                           # 核心指令（触发规则 + 工作流 + 输出模板）
├── scripts/
│   ├── fetch_rss.py                   # RSS 采集（21 个内置源，并行抓取）
│   └── fetch_hackernews.py            # HN API 采集（零外部依赖）
└── references/
    ├── sources_registry.md            # 完整信源注册表（120+ 源）
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
| RSS 采集（公司官方） | 6/9 源成功（OpenAI, DeepMind, Google AI, Microsoft, HuggingFace, NVIDIA） |
| RSS 采集（行业媒体） | 7/8 源成功（量子位, 36氪, The Verge, TechCrunch, Ars Technica, MIT, VentureBeat） |
| RSS 采集（学术平台） | 2/3 源成功（arXiv cs.AI, arXiv cs.CL） |
| HN API 采集 | 成功 |
| 全源采集 | 59 篇文章 / 13 个活跃源 / 4 种类型 |

## License

MIT
