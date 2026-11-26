mcp-china-sourcing-map/
├── main.py                  # FastMCP 入口：注册全部 7 个工具
├── requirements.txt
├── SKILL.md                 # 上架 mcpmarket 用的 skill 包（英文，海外买家读）
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py            # 数据源开关（合规源默认开，1688 增强层默认关）
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── public_web.py    # 公开源：1688/国际站只读公开展示信息（不存库）
│   │   ├── tariff.py        # USITC HTS 关税行（免费）+ 汇率公开接口
│   │   └── logistics.py     # 物流/关税/趋势 占位适配器
│   └── tools/
│       ├── __init__.py
│       ├── find_factory.py  # 按品类/地区找工厂
│       ├── price_compare.py # 同款多供应商比价
│       ├── moq_check.py     # 起订量/交期/运费查询
│       ├── supplier_verify.py# 供应商资质/信用/出口记录
│       ├── shipping_quote.py# 海运/空运/快递报价
│       ├── duty_calc.py     # 目标国关税估算
│       └── trend_hot.py     # 海外热销品类趋势
└── tests/
    └── test_tools.py        # 离线可跑（mock 数据源），pytest 验证
