from __future__ import annotations
import logging
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .config import load_settings
from .connectors.erpcom import ErpComConnector
from .connectors.operaciones import ErpOpsConnector
from .models import DailyBrief
from .analyzer.ceo_brain import analyze
from .notifier.whatsapp import format_report, send_whatsapp
from .storage.history import save_brief, save_report, load_recent_briefs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("ceo-app")


def build_brief(settings, for_date: date) -> DailyBrief:
    erpcom = ErpComConnector(settings.erpcom_base_url, settings.erpcom_api_key)
    erpops = ErpOpsConnector(settings.erpops_base_url, settings.erpops_api_key)
    try:
        log.info("Fetching sales + finance from erpcom...")
        sales = erpcom.fetch_sales(for_date)
        finance = erpcom.fetch_finance(for_date)
        log.info("Fetching inventory + operations from operaciones...")
        inventory = erpops.fetch_inventory(for_date)
        operations = erpops.fetch_operations(for_date)
    finally:
        erpcom.close()
        erpops.close()

    return DailyBrief(
        brief_date=for_date,
        sales=sales,
        inventory=inventory,
        operations=operations,
        finance=finance,
    )


def run() -> int:
    settings = load_settings()
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()

    log.info("CEO daily run for %s (tz=%s)", today, settings.timezone)

    brief = build_brief(settings, today)
    save_brief(settings.history_dir, brief)
    log.info("Brief stored. Loading last 14 days of history...")

    history = load_recent_briefs(settings.history_dir, days=14, before=today)
    log.info("History points: %d", len(history))

    report = analyze(
        api_key=settings.anthropic_api_key,
        model=settings.claude_model,
        today=brief,
        history=history,
    )
    save_report(settings.history_dir, report)
    log.info("CEO report generated. Semaforo=%s, insights=%d",
             report.semaforo, len(report.insights))

    body = format_report(report)
    log.info("Sending WhatsApp to %s...", settings.whatsapp_to)
    send_whatsapp(
        token=settings.whatsapp_token,
        phone_number_id=settings.whatsapp_phone_number_id,
        to=settings.whatsapp_to,
        body=body,
    )
    log.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
