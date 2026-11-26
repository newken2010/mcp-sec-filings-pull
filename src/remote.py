"""官方 MCP Server 直连（不自己写 HTTP 封装）。

- 天眼查：https://mcp.tianyancha.com/v1      Header: Authorization: Bearer <token>
- 快递100：http://api.kuaidi100.com/mcp/sse?key=<key>   (SSE)

key 全部走环境变量；没配 key 的 server 不挂载，项目零凭据也能启动。
挂载后工具名带前缀：`tianyancha_*` / `kuaidi100_*`。
"""
from __future__ import annotations
import os
from urllib.parse import quote

from fastmcp import FastMCP

TIANYANCHA_URL = "https://mcp.tianyancha.com/v1"
KUAIDI100_URL = "http://api.kuaidi100.com/mcp/sse"


def remote_server_configs() -> dict:
    """按已配置的 key 生成 MCPConfig（mcpServers）条目。"""
    servers: dict[str, dict] = {}

    tyc_token = os.environ.get("TIANYANCHA_TOKEN", "").strip()
    if tyc_token:
        servers["tianyancha"] = {
            "url": os.environ.get("TIANYANCHA_MCP_URL", TIANYANCHA_URL),
            "transport": "http",
            "headers": {"Authorization": f"Bearer {tyc_token}"},
        }

    kd_key = os.environ.get("KUAIDI100_KEY", "").strip()
    if kd_key:
        base = os.environ.get("KUAIDI100_MCP_URL", KUAIDI100_URL)
        sep = "&" if "?" in base else "?"
        servers["kuaidi100"] = {
            "url": f"{base}{sep}key={quote(kd_key, safe='')}",
            "transport": "sse",
        }

    return servers


def mount_remote_servers(mcp: FastMCP) -> list[str]:
    """把已配置的远程 MCP 挂到主 server 上，返回挂载成功的名字。"""
    servers = remote_server_configs()
    if not servers:
        return []
    proxy = FastMCP.as_proxy({"mcpServers": servers}, name="remote-connectors")
    mcp.mount(proxy)
    return sorted(servers)
