# TOOLS.md — Stock Expert Environment

## System Environment

### Platform Support
- **macOS / Linux**: Bash / zsh (fully supported)
- **Windows**: PowerShell 5.1+ (default on Windows 10/11)
- **Python**: 3.11+ (managed by your ClawDI platform)
- **Package Manager**: `uv` (Python package runner — auto-installs dependencies)

### Critical Constraints by Platform

**macOS / Linux (Bash):**
- Use `&&` for command chaining ✅
- Example: `cd dir && python script.py`

**Windows PowerShell:**
- Use `;` for command chaining, NOT `&&`
- ✅ `cd dir; python script.py`
- ❌ `cd dir && python script.py`
- For A-share output: prefix with `$env:PYTHONIOENCODING='utf-8';`

### Chart Generation
- stock-info-explorer outputs **text reports only**
- Do NOT attempt to generate PNG charts (disabled)

---

## Python Libraries

| Library | Purpose | Markets |
|---------|---------|---------|
| `yfinance` | Yahoo Finance data — quotes, fundamentals, history | US · A-share · HK · Global |
| `akshare` | A-share data — Eastmoney announcements | A-share only |
| `requests` | SEC EDGAR API calls | US only |
| `pandas`, `numpy` | Data processing | All |
| `matplotlib` | ⚠️ Installed but NOT used (text-only mode) | — |

---

## Stock Ticker Formats

### US Stocks (NYSE / NASDAQ / AMEX)
- Format: `TICKER` (no suffix)
- Examples: `AAPL`, `TSLA`, `NVDA`, `MSFT`, `AMZN`, `GOOGL`, `META`

### A-Share — Shanghai Stock Exchange (SSE)
- Format: `XXXXXX.SS`
- Examples: `600519.SS` (Kweichow Moutai), `601318.SS` (Ping An), `600036.SS` (CMB)

### A-Share — Shenzhen Stock Exchange (SZSE)
- Format: `XXXXXX.SZ`
- Examples: `000001.SZ` (Ping An Bank), `002594.SZ` (BYD), `000002.SZ` (Vanke)

### Hong Kong Stocks (HKEX)
- Format: `XXXX.HK`
- Examples: `0700.HK` (Tencent), `9988.HK` (Alibaba), `0005.HK` (HSBC)

### Cryptocurrency
- Format: `COIN-USD`
- Examples: `BTC-USD`, `ETH-USD`, `SOL-USD`

### Forex
- Format: `XXXYYY=X`
- Examples: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`

---

## Skill Command Reference

### stock-deep-analyzer

**macOS / Linux:**
```bash
# US stock deep analysis
uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py NVDA

# A-share deep analysis
uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py 600519.SS

# Custom period
uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py AAPL --period 1y
```

**Windows PowerShell:**
```powershell
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py NVDA
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-deep-analyzer/scripts/deep_analyze.py 600519.SS --period 1y
```

---

### stock-announcement-fetcher

Auto-routes by ticker format:
- No suffix → **SEC EDGAR** (US)
- `.SS` / `.SZ` / 6-digit code → **AkShare / Eastmoney** (A-share)

**macOS / Linux:**
```bash
# US — SEC EDGAR
uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py AAPL
uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py TSLA --days 7

# A-share — Eastmoney
uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py 600519 --days 7
uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py 000001.SZ
```

**Windows PowerShell:**
```powershell
# US
uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py AAPL --days 30

# A-share
$env:PYTHONIOENCODING='utf-8'; uv run --script skills/stock-announcement-fetcher/scripts/fetch_announcements.py 600519 --days 7
```

---

### stock-info-explorer

```bash
# Real-time quote
uv run --script skills/stock-info-explorer/scripts/yf.py price TSLA
uv run --script skills/stock-info-explorer/scripts/yf.py price 000001.SZ

# Comprehensive report
uv run --script skills/stock-info-explorer/scripts/yf.py report NVDA 6mo

# Technical analysis with indicators
uv run --script skills/stock-info-explorer/scripts/yf.py pro AAPL 6mo --rsi --macd --bb --vwap
```

---

### trading-coach

```bash
uv run --script skills/trading-coach/scripts/analyze_trades.py --file path/to/trades.csv
```

Supported broker CSV formats: IBKR · Schwab · TD Ameritrade · Robinhood · Webull · Futu · Tiger · CITIC · Huatai

---

## Debugging Tips

### Common Issues

1. **`&&` is not valid** (Windows only)
   - Cause: Bash syntax used in PowerShell
   - Fix: Replace `&&` with `;`

2. **A-share output shows garbled characters** (Windows only)
   - Cause: PowerShell GBK encoding
   - Fix: Prefix with `$env:PYTHONIOENCODING='utf-8';`
   - Note: US stock output is unaffected

3. **No module named matplotlib / chart generation fails**
   - Cause: Agent attempting to generate PNG
   - Fix: Use `report` or `pro` commands (text-only mode)

4. **Tool call timeout / terminated**
   - Cause: Long-running write operations
   - Fix: Break into smaller steps, use workdir parameter

5. **SEC EDGAR rate limit**
   - Cause: Too many rapid requests to SEC API
   - Fix: Add a short delay between requests; SEC allows ~10 req/sec

---

**Last Updated**: 2026-03-23  
**Tested On**: Python 3.11+, uv 0.5.x, macOS 14 / Windows PowerShell 5.1
