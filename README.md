# 股票专家 Agent (stockexpert-1)

> 专业AI助手，专注于A股公告追踪、全球股市分析和交易复盘。提供数据驱动的投资决策参考。

## 快速部署到 EasyClaw

### Step 1：克隆仓库

```bash
git clone https://github.com/xiaolu7586/stockexpert-agent.git
cd stockexpert-agent
```

### Step 2：将 workspace 复制到 EasyClaw 目录

**macOS / Linux:**
```bash
cp -r . ~/.easyclaw/workspace-stockexpert-1
```

**Windows:**
```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.easyclaw\workspace-stockexpert-1"
```

### Step 3：将 agent 配置写入 `easyclaw.json`

打开 `~/.easyclaw/easyclaw.json`（Windows：`%USERPROFILE%\.easyclaw\easyclaw.json`），在 `agents.list` 数组中追加 `easyclaw-agent.json` 的内容，并将 `workspace` 字段改为你本机的实际路径：

```json
{
  "id": "stockexpert-1",
  "name": "股票专家",
  "description": "专业AI助手，专注于A股公告追踪、全球股市分析和交易复盘。提供数据驱动的投资决策参考。",
  "model": "easyclaw/claude.sonnet-4.6",
  "workspace": "/YOUR_HOME/.easyclaw/workspace-stockexpert-1",
  "skills": [
    "stock-announcement-fetcher",
    "trading-coach",
    "stock-info-explorer",
    "stock-deep-analyzer"
  ],
  "tools": {
    "allow": ["group:subagent"]
  }
}
```

### Step 4：重启 EasyClaw Gateway

配置写入后无需重启 session，Gateway 会自动加载新 agent。

---

## 核心能力

| Skill | 用途 | 数据源 |
|---|---|---|
| **stock-deep-analyzer** ⭐ | 一键深度分析（价值+技术+成长+财务评分） | Yahoo Finance |
| **stock-announcement-fetcher** | A股上市公司公告监控 | 东方财富 (AkShare) |
| **stock-info-explorer** | 实时行情 + 技术指标文本报告 | Yahoo Finance |
| **trading-coach** | 券商CSV交易复盘（8维度评分+10维洞察） | 本地CSV |

## Python 依赖

```bash
# stock-deep-analyzer & stock-info-explorer
pip install yfinance pandas numpy rich plotille

# stock-announcement-fetcher
pip install akshare pandas PyPDF2 requests

# 推荐使用 uv 运行（自动管理依赖）
# https://github.com/astral-sh/uv
```

## 常用命令（Windows PowerShell 环境）

```powershell
# 深度分析（首选）
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py 601288.SS

# 实时行情
uv run --script skills/stock-info-explorer/scripts/yf.py price 600519.SS

# 技术指标报告
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-info-explorer/scripts/yf.py pro 000001.SZ 6mo --rsi --macd --bb

# A股公告查询
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py 600519 --days 7
```

## 目录结构

```
stockexpert-agent/
├── easyclaw-agent.json                              # Agent 配置（写入 easyclaw.json 使用）
├── AGENTS.md                                        # Agent 系统指令
├── TOOLS.md                                         # 环境配置说明
└── skills/
    ├── stock-deep-analyzer/
    │   ├── SKILL.md
    │   └── scripts/deep_analyze.py
    ├── stock-announcement-fetcher/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── fetch_announcements.py
    │   │   └── fetch_announcements_multi_source.py
    │   └── references/
    │       ├── cninfo-api.md
    │       ├── tushare-guide.md
    │       └── upgrade-guide.md
    ├── stock-info-explorer/
    │   ├── SKILL.md
    │   ├── _meta.json
    │   └── scripts/yf.py
    └── trading-coach/
        ├── SKILL.md
        ├── _meta.json
        └── references/
            ├── csv_formats.md
            ├── scoring_system.md
            └── insight_dimensions.md
```
