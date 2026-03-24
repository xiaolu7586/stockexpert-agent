---
name: trading-coach
description: |
  AI trade review coach — turn your broker's CSV export into actionable improvement insights.
  Supports US brokers (IBKR, Schwab, TD Ameritrade, Robinhood, Webull) and Asian brokers (Futu/Moomoo, Tiger, CITIC, Huatai).
  Automatic FIFO position matching, 8-dimension quality scoring, 10-dimension AI insights.
  Trigger when: user provides a trading CSV, asks to analyze trade performance, review trades,
  calculate P&L statistics, identify trading patterns, or says "review my trades" / "analyze my trading".
---

# 🏆 Trading Coach — AI Trade Review

> Stop trading on gut feel. Let data show you what's working and what needs to change.

Transform your broker's CSV trade history into a **professional review report** and **actionable improvement recommendations**.

## ✨ Core Capabilities

- 🔄 **Smart Import** — Auto-detects broker format from supported brokers
- 📊 **FIFO Matching** — Automatically pairs buys and sells into complete position cycles
- 🎯 **8-Dimension Scoring** — Entry, exit, trend, risk, market context, behavior, news fit, execution
- 💡 **AI Insights** — 10-dimension analysis that surfaces your trading blind spots

## 🚀 Quick Start

```bash
# Review your trades
uv run --script skills/trading-coach/scripts/analyze_trades.py --file path/to/trades.csv
```

## 📈 Supported Brokers

### US & International
| Broker | Format | Notes |
|--------|--------|-------|
| Interactive Brokers (IBKR) | Activity Statement CSV | Use "Trades" section |
| Charles Schwab | Trade History CSV | Export from Transaction History |
| TD Ameritrade / thinkorswim | Transaction History CSV | |
| Robinhood | Account CSV export | Download from app |
| Webull | Transactions CSV | Export from Order History |

### Asian Brokers
| Broker | Encoding | Detection fields |
|--------|----------|-----------------|
| Futu / Moomoo (English) | UTF-8 | Side, Symbol, Fill Time |
| Futu / Moomoo (Chinese) | UTF-8-BOM | 方向, 代码, 成交时间 |
| Tiger Brokers | UTF-8 | 交易方向, 股票代码 |
| CITIC Securities | GBK | 买卖标志, 证券代码 |
| Huatai Securities | GBK | 操作, 证券代码 |

See [references/csv_formats.md](references/csv_formats.md) for full field specifications.

## 🎯 Scoring System

8 dimensions, each weighted:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Entry quality | 18% | Timing and technical indicator alignment |
| Exit quality | 17% | Stop-loss and take-profit execution |
| Trend alignment | 14% | Trading with or against the trend (ADX) |
| Risk management | 12% | R:R ratio, MAE/MFE control |
| Market context | 11% | Market condition fit at entry |
| Trading behavior | 11% | Discipline, impulse detection |
| News fit | 7% | Consistency with news/events backdrop |
| Execution quality | 5% | Slippage, fill efficiency |

**Grades**: A (90+) / B (80–89) / C (70–79) / D (60–69) / F (<60)

See [references/scoring_system.md](references/scoring_system.md) for full details.

## 💡 AI Insights

10-dimension deep analysis of your trading patterns:

1. Entry analysis
2. Exit analysis
3. Risk control
4. Holding duration
5. Fee drag
6. Historical comparison
7. Pattern recognition
8. Root cause analysis
9. Event correlation
10. Improvement recommendations

See [references/insight_dimensions.md](references/insight_dimensions.md) for full details.

## 📊 Sample Output

```
Total positions: 150  |  Win rate: 62.5%  |  Total P&L: +$12,500  |  Avg score: 72.3 (C)

⚠️  Buying overbought conditions — RSI was 75.2 at entry; avoid chasing when RSI > 70
✅  Stop-loss discipline is solid — avg loss controlled at 2.3%
💡  Holding periods are short — avg 2.3 days; consider letting winners run longer
```
