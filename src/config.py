import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    claude_model: str
    erpcom_base_url: str
    erpcom_api_key: str
    erpops_base_url: str
    erpops_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_from: str
    twilio_whatsapp_to: str
    timezone: str
    history_dir: str


def _req(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def load_settings() -> Settings:
    return Settings(
        anthropic_api_key=_req("ANTHROPIC_API_KEY"),
        claude_model=os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
        erpcom_base_url=_req("ERPCOM_BASE_URL"),
        erpcom_api_key=_req("ERPCOM_API_KEY"),
        erpops_base_url=_req("ERPOPS_BASE_URL"),
        erpops_api_key=_req("ERPOPS_API_KEY"),
        twilio_account_sid=_req("TWILIO_ACCOUNT_SID"),
        twilio_auth_token=_req("TWILIO_AUTH_TOKEN"),
        twilio_whatsapp_from=_req("TWILIO_WHATSAPP_FROM"),
        twilio_whatsapp_to=_req("TWILIO_WHATSAPP_TO"),
        timezone=os.environ.get("TIMEZONE", "America/Mexico_City"),
        history_dir=os.environ.get("HISTORY_DIR", "data/history"),
    )
