"""Config: read-only public SEC EDGAR only; nothing persisted beyond the
ticker-map cache. Enterprise data vendors are out of scope for v1."""
from dataclasses import dataclass


@dataclass
class Config:
    user_agent: str = "mcp-sec-filings-pull/0.1 (research; contact: agent@example.com)"
    min_interval_s: float = 0.12   # SEC etiquette: <=10 req/s
    max_filings_per_ticker: int = 200


def get_config() -> Config:
    return Config()