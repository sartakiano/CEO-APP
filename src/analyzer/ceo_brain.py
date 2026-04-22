from __future__ import annotations
import json
from anthropic import Anthropic
from ..models import DailyBrief, CEOReport
from .prompts import CEO_SYSTEM_PROMPT, OUTPUT_SCHEMA_HINT


def analyze(
    api_key: str,
    model: str,
    today: DailyBrief,
    history: list[DailyBrief],
) -> CEOReport:
    """Envia el brief del dia + historico a Claude y devuelve el CEOReport.

    Usa prompt caching en el system prompt y el esquema (contenido estable)
    para abaratar la corrida diaria."""
    client = Anthropic(api_key=api_key)

    history_payload = [b.model_dump(mode="json") for b in history]
    today_payload = today.model_dump(mode="json")

    user_content = (
        "Analiza el cierre del dia y emite el brief del CEO.\n\n"
        f"== HISTORICO ({len(history_payload)} dias previos) ==\n"
        f"{json.dumps(history_payload, ensure_ascii=False, default=str)}\n\n"
        "== CIERRE DE HOY ==\n"
        f"{json.dumps(today_payload, ensure_ascii=False, default=str)}\n"
    )

    resp = client.messages.create(
        model=model,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": CEO_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": OUTPUT_SCHEMA_HINT,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": user_content}],
    )

    text = "".join(block.text for block in resp.content if block.type == "text").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    data = json.loads(text)
    data["brief_date"] = today.brief_date
    return CEOReport.model_validate(data)
