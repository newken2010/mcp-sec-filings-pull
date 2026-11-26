# mcp-china-sourcing-map

中国供应链地图 MCP：一个工具集帮海外买家端到端规划一次中国采购
（找厂 → 比价 → MOQ → 验供应商 → 运费 → 关税 → 热销趋势）。

合规优先：默认只用公开数据源，**不存储任何供应商细节**；1688/阿里/物流
的企业 API 是可插拔增强层（需企业资质），没资质也能跑。

## 快速开始
```bash
pip install -r requirements.txt
python main.py            # stdio MCP server
pytest tests/ -q          # 离线验证（mock 数据源）
```

## 结构
见 `ARCHITECTURE.md`。7 个工具在 `src/tools/`，数据源在 `src/sources/`，
统一响应壳 `{data, source, dataQuality, disclaimer, locale}` 在 `src/envelope.py`。

## 数据源实况（别把 guidance 当数据卖）

| 工具 | 现在能返回真实数据吗 | 缺什么 |
|---|---|---|
| `duty_calc` | ✅ 美国目的国（USITC HTS，免 key） | 其他国家没有免费公开关税 API |
| `find_factory` / `price_compare` | ❌ 只返回 guidance | 1688 开放平台 / 阿里国际站企业资质，或 BigGo API key |
| `moq_check` | ❌ 只返回 guidance | offer 页读取适配器，或上面的企业 API |
| `supplier_verify` | ❌ 只返回核验清单 | 企业信用 / 海关出口数据源（多为付费） |
| `shipping_quote` | ❌ 只返回 guidance | 顺丰国际 / 递四方 / 燕文企业 key |
| `trend_hot` | ❌ 只返回 guidance | 国际站趋势接口或 BigGo |

没有 key 的工具一律 `dataQuality=degraded`，**不会编造供应商、价格、运价**。

## 输出语言（全英文 + 按目的地切语言）
面向海外买家的文案**默认全英文**。每个工具都有 `locale` 参数
（`en`/`de`/`fr`/`es`/`ja`/`ko`）切换 disclaimer/指引文案；
`duty_calc` / `shipping_quote` 在省略 `locale` 时按 `destination` 国家
自动选语言（如 `DE`→德文、`JP`→日文）。无翻译的 locale 回退英文，
绝不输出半拉子多语言；数据字段保持源语言。
`supplier_verify` 的核验步骤（verify_steps）也随 locale 切换六语。

## 合规红线（卖之前必读）
- 只读公开展示字段，不爬私有数据、不落库。
- 关税输出=规划估算，必须提示"找持牌报关行确认"。
- 1688/阿里/顺丰/递四方/燕文开放 API 需**企业资质**，个人号权限有限——
  所以默认走公开源，增强层等你有资质再插。
- 供应商数据涉及商业信息，**别存太细**（本仓不落库）。
