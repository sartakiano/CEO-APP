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
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_to: str
    whatsapp_template_name: str
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
        whatsapp_token=_req("WHATSAPP_TOKEN"),
        whatsapp_phone_number_id=_req("WHATSAPP_PHONE_NUMBER_ID"),
        whatsapp_to=_req("WHATSAPP_TO"),
        whatsapp_template_name=os.environ.get("WHATSAPP_TEMPLATE_NAME", ""),
        timezone=os.environ.get("TIMEZONE", "America/Mexico_City"),
        history_dir=os.environ.get("HISTORY_DIR", "data/history"),
    )
