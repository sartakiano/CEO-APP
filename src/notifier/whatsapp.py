from __future__ import annotations
import httpx
from ..models import CEOReport


EMOJI = {"rojo": "ROJO", "amarillo": "AMARILLO", "verde": "VERDE"}
SEV = {
    "critico": "[CRITICO]",
    "alto": "[ALTO]",
    "medio": "[MEDIO]",
    "informativo": "[INFO]",
}


def format_report(report: CEOReport) -> str:
    """Formato compacto para WhatsApp (1500 chars aprox). Sin markdown pesado."""
    lines: list[str] = []
    lines.append(f"*Brief CEO {report.brief_date.isoformat()}* — {EMOJI.get(report.semaforo, report.semaforo).upper()}")
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
    return text[:3900]  # limite del body de WhatsApp


def send_whatsapp(
    token: str,
    phone_number_id: str,
    to: str,
    body: str,
) -> dict:
    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    r = httpx.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()
