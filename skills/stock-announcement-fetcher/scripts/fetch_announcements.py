#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["akshare", "pandas", "requests"]
# ///
"""
Stock Announcement Fetcher
--------------------------
Fetches corporate announcements and regulatory filings.

Market routing (auto-detected from ticker format):
  - US stocks (AAPL, TSLA, NVDA)  → SEC EDGAR
  - A-share (600519, 000001.SZ)   → AkShare / Eastmoney
"""

import argparse
import re
import sys
import time
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Market detection
# ---------------------------------------------------------------------------

def detect_market(ticker: str) -> str:
    """Return 'us' or 'cn' based on ticker format."""
    ticker = ticker.strip().upper()
    # A-share: 6-digit code optionally followed by .SS or .SZ
    if re.match(r"^\d{6}(\.SS|\.SZ)?$", ticker, re.IGNORECASE):
        return "cn"
    # Explicit A-share suffix
    if ticker.endswith(".SS") or ticker.endswith(".SZ"):
        return "cn"
    # Everything else treated as US
    return "us"


def normalize_cn_code(ticker: str) -> str:
    """Strip .SS / .SZ suffix and return bare 6-digit code."""
    return re.sub(r"\.(SS|SZ)$", "", ticker.strip(), flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# US: SEC EDGAR
# ---------------------------------------------------------------------------

SEC_HEADERS = {
    "User-Agent": "StockExpertAgent contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}

FILING_TYPE_LABELS = {
    "8-K":    "Material Event",
    "10-K":   "Annual Report",
    "10-Q":   "Quarterly Report",
    "S-1":    "IPO Registration",
    "DEF 14A": "Proxy Statement",
    "SC 13G": "Large Shareholder (passive)",
    "SC 13D": "Large Shareholder (active)",
    "4":      "Insider Transaction",
}


def get_cik(ticker: str) -> str | None:
    """Resolve ticker to SEC CIK number."""
    import requests
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"
    # Faster: use company_tickers.json
    resp = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=SEC_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)
    return None


def fetch_sec_filings(ticker: str, days: int = 30, filing_type: str | None = None) -> list[dict]:
    """Fetch recent SEC filings for a US ticker via EDGAR."""
    import requests

    print(f"Fetching SEC EDGAR filings for {ticker}...")

    cik = get_cik(ticker)
    if not cik:
        print(f"  ⚠️  Could not resolve {ticker} to a CIK. "
              "Check ticker spelling or try the SEC EDGAR search at https://www.sec.gov/cgi-bin/browse-edgar")
        return []

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=SEC_HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    company_name = data.get("name", ticker)
    recent = data.get("filings", {}).get("recent", {})

    forms       = recent.get("form", [])
    filed_dates = recent.get("filingDate", [])
    accessions  = recent.get("accessionNumber", [])
    descriptions = recent.get("primaryDocument", [])

    cutoff = datetime.now() - timedelta(days=days)
    results = []

    for form, date_str, accession, doc in zip(forms, filed_dates, accessions, descriptions):
        try:
            filed = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if filed < cutoff:
            continue
        if filing_type and form.upper() != filing_type.upper():
            continue

        acc_clean = accession.replace("-", "")
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{acc_clean}/{doc}"
        )
        results.append({
            "date": date_str,
            "type": form,
            "label": FILING_TYPE_LABELS.get(form, form),
            "title": f"{form} — {FILING_TYPE_LABELS.get(form, 'SEC Filing')}",
            "url": url,
            "company": company_name,
        })

    return results


def print_sec_results(ticker: str, filings: list[dict]) -> None:
    sep = "=" * 80
    print(sep)
    company = filings[0]["company"] if filings else ticker
    print(f"SEC Filings: {company} ({ticker.upper()})")
    print(f"Source: SEC EDGAR  |  https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}")
    print(sep)
    if not filings:
        print("No filings found in the specified date range.")
        return
    for i, f in enumerate(filings, 1):
        print(f"\n[{i}] {f['date']}")
        print(f"    Type:  {f['type']} ({f['label']})")
        print(f"    Title: {f['title']}")
        print(f"    URL:   {f['url']}")
    print()


# ---------------------------------------------------------------------------
# A-share: AkShare / Eastmoney
# ---------------------------------------------------------------------------

def fetch_cn_announcements(ticker: str, days: int = 30, keyword: str | None = None) -> list[dict]:
    """Fetch A-share announcements via AkShare / Eastmoney."""
    import akshare as ak
    import pandas as pd

    code = normalize_cn_code(ticker)
    print(f"Fetching A-share announcements for {code} (Eastmoney)...")

    today = datetime.now().date()
    cutoff = today - timedelta(days=days)

    try:
        df = ak.stock_notice_report(symbol="全部")
    except Exception as e:
        print(f"  ⚠️  Failed to fetch announcements: {e}")
        return []

    if df is None or df.empty:
        return []

    # Filter by stock code
    code_cols = [c for c in df.columns if "代码" in c or "code" in c.lower()]
    if code_cols:
        df = df[df[code_cols[0]].astype(str).str.contains(code)]

    # Filter by date
    date_cols = [c for c in df.columns if "时间" in c or "日期" in c or "date" in c.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
        df = df[df[date_cols[0]].dt.date >= cutoff]

    # Filter by keyword
    title_cols = [c for c in df.columns if "标题" in c or "title" in c.lower()]
    if keyword and title_cols:
        df = df[df[title_cols[0]].str.contains(keyword, na=False)]

    results = []
    for _, row in df.iterrows():
        results.append({
            "date": str(row.get(date_cols[0], "")[:10]) if date_cols else "",
            "title": str(row.get(title_cols[0], "")) if title_cols else str(row.iloc[0]),
            "type": str(row.get("公告类型", "")),
            "url": str(row.get("URL", row.get("链接", ""))),
        })

    return results


def print_cn_results(ticker: str, announcements: list[dict]) -> None:
    sep = "=" * 80
    print(sep)
    print(f"Announcements: {ticker}")
    print("Source: Eastmoney (AkShare)")
    print(sep)
    if not announcements:
        print("No announcements found in the specified date range.")
        return
    for i, a in enumerate(announcements, 1):
        print(f"\n[{i}] {a['date']}")
        print(f"    Title: {a['title']}")
        if a["type"]:
            print(f"    Type:  {a['type']}")
        if a["url"]:
            print(f"    URL:   {a['url']}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch corporate announcements and SEC filings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # US — SEC EDGAR
  uv run --script fetch_announcements.py AAPL
  uv run --script fetch_announcements.py TSLA --days 7
  uv run --script fetch_announcements.py NVDA --type 10-Q

  # A-share — Eastmoney
  uv run --script fetch_announcements.py 600519 --days 7
  uv run --script fetch_announcements.py 000001.SZ --keyword earnings
        """,
    )
    parser.add_argument("ticker", help="Stock ticker (e.g. AAPL, TSLA, 600519, 000001.SZ)")
    parser.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
    parser.add_argument("--type", dest="filing_type", default=None,
                        help="US only: filing type filter (e.g. 8-K, 10-K, 10-Q)")
    parser.add_argument("--keyword", default=None, help="A-share only: keyword filter for announcement titles")
    parser.add_argument("--format", dest="fmt", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    market = detect_market(args.ticker)

    if market == "us":
        results = fetch_sec_filings(args.ticker, days=args.days, filing_type=args.filing_type)
        if args.fmt == "json":
            import json
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_sec_results(args.ticker, results)
    else:
        results = fetch_cn_announcements(args.ticker, days=args.days, keyword=args.keyword)
        if args.fmt == "json":
            import json
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_cn_results(args.ticker, results)


if __name__ == "__main__":
    main()
