---
name: china-sourcing-map
description: China supply-chain sourcing MCP — find factories, compare prices, check MOQ, verify suppliers, get shipping/duty estimates, and track hot categories. Compliance-first: public sources only by default, no supplier details persisted.
version: 0.1.0
entrypoint: main.py
runtime: python>=3.11
---

# China Sourcing Map (MCP)

Give your AI agent one tool to plan a China sourcing move end to end:
**find factory → price compare → MOQ → verify supplier → shipping quote →
duty estimate → hot-category trend.**

## Why this exists
Chinese supply chain is strong but opaque to overseas buyers. This MCP
packages the public, low-risk data sources into one agent-friendly tool set,
with a clean "degraded" marker instead of invented data when a live source
isn't configured.

## Tools (7)
| Tool | Purpose | Live data requires |
|---|---|---|
| `find_factory` | factories/suppliers for a category+region | 1688/国际站 public or API |
| `price_compare` | multi-supplier price for same category | public listings / BigGo |
| `moq_check` | MOQ / lead time / freight for an offer | public display fields |
| `supplier_verify` | credit + customs + trade-feedback signals | public 信用公示 |
| `shipping_quote` | sea/air/express quote | logistics API key |
| `duty_calc` | duty/tariff by HS code | USITC HTS API (free, US lines) |
| `trend_hot` | overseas hot-category signal | 国际站 public trend |

Every tool returns a standard envelope: `{data, source, dataQuality, disclaimer, locale}`.
`dataQuality=degraded` means "no live source configured — here's guidance,
not a fabricated answer."

## Output language (`locale`)
Buyer-facing copy defaults to **English**. Every tool accepts `locale`
(`en`/`de`/`fr`/`es`/`ja`/`ko`) to switch the disclaimer + guidance text.
For `duty_calc` / `shipping_quote`, if `locale` is omitted the `destination`
country auto-selects the language (e.g. `destination="DE"` → German copy,
`destination="JP"` → Japanese). Untranslated locales fall back to English —
we never emit half-localised text. Data fields keep their source language.

Example: `duty_calc(hs_code="8471.30", origin="CN", destination="DE")`
returns the tariff note in German with `"locale": "de"`.

## Run
```bash
pip install -r requirements.txt
python main.py          # stdio MCP server
pytest tests/ -q       # offline, mocks data sources
```

## MCP client config (example, Claude Desktop / Cursor)
```json
{
  "mcpServers": {
    "china-sourcing-map": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/mcp-china-sourcing-map"
    }
  }
}
```

## Enterprise enhancement (optional, needs 企业资质)
- `cfg.alibaba_1688_api = True` → authoritative 1688 product/supplier
- `cfg.alibaba_intl_api = True` → 阿里国际站 cross-border products
- `cfg.biggo = True` → BigGo-MCP (MIT) cross-platform price + history
- logistics API key → live shipping quotes

## Compliance notes (read before selling)
- Publicly displayed supplier fields only; **no off-platform or private data stored**.
- Tariff output is a planning estimate — buyers must confirm with a licensed
  customs broker.
- 1688/阿里/顺丰/递四方/燕文 open APIs require **enterprise credentials**; the
  public fallback is intentional so the server works with zero keys.
- Always surface the `disclaimer` field to end users.
