import pandas as pd
import yfinance as yf
from datetime import datetime
from tabulate import tabulate


def load_trades(path="trades.csv"):
    df = pd.read_csv(path)
    df["Trade Type"] = df["Trade Type"].str.lower().str.strip()
    df["Trade Date"] = pd.to_datetime(df["Trade Date"])
    return df.sort_values("Trade Date")


def compute_holdings(df):
    holdings = {}
    for symbol, group in df.groupby("Symbol"):
        lots, realised = [], 0.0
        for _, row in group.iterrows():
            qty, price = row["Quantity"], row["Price"]
            if row["Trade Type"] == "buy":
                lots.append([qty, price])
            elif row["Trade Type"] == "sell":
                left = qty
                while left > 0 and lots:
                    if lots[0][0] <= left:
                        realised += lots[0][0] * (price - lots[0][1])
                        left -= lots[0].pop(0) or lots.pop(0)[0]
                    else:
                        realised += left * (price - lots[0][1])
                        lots[0][0] -= left
                        left = 0

        qty_held = sum(l[0] for l in lots)
        cost     = sum(l[0] * l[1] for l in lots)
        holdings[symbol] = {
            "qty":          qty_held,
            "avg_buy":      round(cost / qty_held, 2) if qty_held else 0,
            "cost_basis":   round(cost, 2),
            "realised_pnl": round(realised, 2),
        }
    return {s: h for s, h in holdings.items() if h["qty"] > 0}


def fetch_prices(symbols):
    prices = {}
    for s in symbols:
        try:
            t = yf.Ticker(f"{s}.NS").fast_info
            prices[s] = round(float(t.last_price or t.previous_close), 2)
            print(f"  ✓ {s}: ₹{prices[s]}")
        except Exception as e:
            print(f"  ✗ {s}: {e}")
            prices[s] = None
    return prices


def build_rows(holdings, prices):
    rows, total_val = [], 0
    for s, h in holdings.items():
        p = prices.get(s)
        if not p:
            continue
        cur_val  = h["qty"] * p
        upnl     = cur_val - h["cost_basis"]
        upnl_pct = upnl / h["cost_basis"] * 100 if h["cost_basis"] else 0
        rows.append({
            "Symbol":         s,
            "Qty":            int(h["qty"]),
            "Avg Buy (₹)":   h["avg_buy"],
            "LTP (₹)":       p,
            "Cost Basis (₹)": h["cost_basis"],
            "Cur Value (₹)":  round(cur_val, 2),
            "Unreal P&L (₹)": round(upnl, 2),
            "Unreal P&L (%)": round(upnl_pct, 2),
            "Real P&L (₹)":  h["realised_pnl"],
            "_val":           cur_val,
        })
        total_val += cur_val

    for r in rows:
        r["Alloc (%)"] = round(r["_val"] / total_val * 100, 2)
        del r["_val"]
    return rows, total_val


def save_html(rows, total_val, holdings, path="portfolio_report.html"):
    unreal   = sum(r["Unreal P&L (₹)"] for r in rows)
    realised = sum(h["realised_pnl"] for h in holdings.values())

    def sign(v): return "+" if v >= 0 else ""
    def cls(v):  return "green" if v >= 0 else "red"

    trs = ""
    for r in rows:
        u, up, rp = r["Unreal P&L (₹)"], r["Unreal P&L (%)"], r["Real P&L (₹)"]
        trs += f"""<tr>
          <td><b>{r['Symbol']}</b><br><small>{r['Qty']} shares</small></td>
          <td>₹{r['Avg Buy (₹)']:,.0f}</td><td>₹{r['LTP (₹)']:,.0f}</td>
          <td>₹{r['Cost Basis (₹)']:,.0f}</td><td>₹{r['Cur Value (₹)']:,.0f}</td>
          <td class="{cls(u)}">{sign(u)}₹{u:,.0f} ({up:+.1f}%)</td>
          <td class="{cls(rp)}">{sign(rp)}₹{rp:,.0f}</td>
          <td>{r['Alloc (%)']:.1f}%</td></tr>"""

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Portfolio Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; color: #111; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .meta {{ color: #888; font-size: 13px; margin-bottom: 24px; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }}
  .card {{ border: 1px solid #e5e5e5; border-radius: 8px; padding: 14px 20px; min-width: 160px; }}
  .card-label {{ font-size: 11px; text-transform: uppercase; color: #888; margin-bottom: 4px; }}
  .card-val {{ font-size: 18px; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 8px 10px; border-bottom: 2px solid #eee; font-size: 11px; text-transform: uppercase; color: #888; }}
  td {{ padding: 12px 10px; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
  small {{ color: #999; }}
  .green {{ color: #2a7d3f; }} .red {{ color: #c0392b; }}
  tr:hover td {{ background: #fafafa; }}

</style></head><body>
<h1> Portfolio Tracker — NSE India</h1>
<div class="meta">Generated: {datetime.now().strftime("%d %b %Y, %I:%M %p")} &nbsp;·&nbsp; {len(rows)} stocks</div>
<div class="cards">
  <div class="card"><div class="card-label">Portfolio Value</div><div class="card-val">₹{total_val:,.0f}</div></div>
  <div class="card"><div class="card-label">Unrealised P&amp;L</div><div class="card-val {cls(unreal)}">{sign(unreal)}₹{unreal:,.0f}</div></div>
  <div class="card"><div class="card-label">Realised P&amp;L</div><div class="card-val {cls(realised)}">{sign(realised)}₹{realised:,.0f}</div></div>
  <div class="card"><div class="card-label">Total P&amp;L</div><div class="card-val {cls(unreal+realised)}">{sign(unreal+realised)}₹{unreal+realised:,.0f}</div></div>
</div>
<table><thead><tr>
  <th>Stock</th><th>Avg Buy</th><th>LTP</th><th>Cost Basis</th>
  <th>Cur Value</th><th>Unrealised P&amp;L</th><th>Realised P&amp;L</th><th>Alloc</th>
</tr></thead><tbody>{trs}</tbody></table>
<p style="margin-top:20px;font-size:11px;color:#bbb">Prices via Yahoo Finance · Not financial advice</p>
</body></html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f" HTML → {path}")


def main():
    print("\n Loading trades...")
    df = load_trades()
    print(f"  {len(df)} trades · {df['Symbol'].nunique()} symbols\n")

    print(" Computing holdings (FIFO)...")
    holdings = compute_holdings(df)
    print(f"   Active: {', '.join(holdings)}\n")

    print("Fetching live prices...")
    prices = fetch_prices(list(holdings))

    rows, total_val = build_rows(holdings, prices)

    # Console
    cols = ["Symbol","Qty","Avg Buy (₹)","LTP (₹)","Cost Basis (₹)",
            "Cur Value (₹)","Unreal P&L (₹)","Unreal P&L (%)","Real P&L (₹)","Alloc (%)"]
    print("\n" + "="*68)
    print("  PORTFOLIO TRACKER — NSE INDIA  |", datetime.now().strftime("%d %b %Y %I:%M %p"))
    print("="*68)
    print(tabulate([{k: r[k] for k in cols} for r in rows],
                   headers="keys", tablefmt="rounded_outline", floatfmt=".2f"))
    unreal   = sum(r["Unreal P&L (₹)"] for r in rows)
    realised = sum(h["realised_pnl"] for h in holdings.values())
    print(f"\n  Portfolio Value : ₹{total_val:,.2f}")
    print(f"  Unrealised P&L  : ₹{unreal:,.2f}")
    print(f"  Realised P&L    : ₹{realised:,.2f}")
    print(f"  Total P&L       : ₹{unreal + realised:,.2f}")
    print("="*68 + "\n")

    # CSV
    pd.DataFrame(rows).to_csv("portfolio_report.csv", index=False)
    print(" CSV → portfolio_report.csv")

    # HTML
    save_html(rows, total_val, holdings)
    print("\n Done!\n")


if __name__ == "__main__":
    main()