"""Runtime configuration, read from environment / a local .env file.

Kept deliberately dependency-light: python-dotenv (already used by rp850-printer)
loads api/.env, then we read plain os.environ. No pydantic-settings needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _load_env() -> None:
    """Load api/.env if python-dotenv is available (no-op otherwise)."""
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - dotenv is a declared dep
        return
    here = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(here, os.pardir, ".env"))


@dataclass
class Settings:
    database_url: str = "sqlite:///./tasks.db"
    print_mode: str = "console"  # "console" | "printer"
    printer_name: str = "POS-80"
    print_width: int = 24
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


def get_settings() -> Settings:
    _load_env()
    origins = os.environ.get("CORS_ORIGINS", "*")
    return Settings(
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./tasks.db"),
        print_mode=os.environ.get("PRINT_MODE", "console").strip().lower(),
        printer_name=os.environ.get("PRINTER_NAME", "POS-80"),
        print_width=int(os.environ.get("PRINT_WIDTH", "24")),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
    )


settings = get_settings()
