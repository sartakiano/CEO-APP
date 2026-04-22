from __future__ import annotations
from twilio.rest import Client
from ..models import CEOReport


EMOJI = {"rojo": "ROJO", "amarillo": "AMARILLO", "verde": "VERDE"}
SEV = {
    "critico": "[CRITICO]",
    "alto": "[ALTO]",
    "medio": "[MEDIO]",
    "informativo": "[INFO]",
}

# WhatsApp permite hasta 4096 chars en el body. Dejamos margen.
MAX_BODY = 3900


def format_report(report: CEOReport) -> str:
    """Formato compacto para WhatsApp. Sin markdown pesado."""
    lines: list[str] = []
    lines.append(
        f"*Brief CEO {report.brief_date.isoformat()}* - "
        f"{EMOJI.get(report.semaforo, report.semaforo).upper()}"
    )
    lines.append("")
    lines.append(report.resumen_ejecutivo.strip())

    km = report.metricas_clave or {}
    if km:
        lines.append("")
        lines.append("*KPIs*")
        for k, v in km.items():
            lines.append(f"- {k}: {v}")

    if report.insights:
        lines.append("")
        lines.append("*Alertas y recomendaciones*")
        for i, ins in enumerate(report.insights, 1):
            tag = SEV.get(ins.severity, ins.severity.upper())
            lines.append(f"{i}. {tag} {ins.titulo} ({ins.area})")
            lines.append(f"   Hallazgo: {ins.hallazgo}")
            lines.append(f"   Recomendacion: {ins.recomendacion}")
            if ins.accion_inmediata:
                lines.append(f"   Accion: {ins.accion_inmediata}")

    text = "\n".join(lines)
    return text[:MAX_BODY]


def send_whatsapp(
    account_sid: str,
    auth_token: str,
    from_: str,
    to: str,
    body: str,
) -> str:
    """Envia mensaje via Twilio WhatsApp. Devuelve el SID del mensaje."""
    client = Client(account_sid, auth_token)
    msg = client.messages.create(from_=from_, to=to, body=body)
    return msg.sid
