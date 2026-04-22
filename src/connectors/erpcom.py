from __future__ import annotations
from datetime import date
from .base import ERPClient
from ..models import SalesKPIs, FinanceKPIs


class ErpComConnector:
    """
    Conector para erpcom.sekufofoods.com (ERP comercial).
    Responsable de: ventas, cobranza, clientes, margen comercial.

    NOTA: los paths de abajo son placeholders. Ajustar segun la doc oficial del ERP.
    Cada metodo ya asume forma de respuesta tipica; si la API devuelve otra estructura,
    se adapta el parseo aqui y el resto del pipeline no cambia.
    """

    def __init__(self, base_url: str, api_key: str):
        self.client = ERPClient(base_url, api_key)

    def fetch_sales(self, on_date: date) -> SalesKPIs:
        # TODO: endpoint real
        data = self.client.get(
            "/reports/daily-sales",
            params={"date": on_date.isoformat()},
        )
        return SalesKPIs(
            revenue_today=float(data.get("revenue_today", 0)),
            revenue_mtd=float(data.get("revenue_mtd", 0)),
            revenue_goal_mtd=float(data.get("revenue_goal_mtd", 0)),
            orders_count=int(data.get("orders_count", 0)),
            avg_ticket=float(data.get("avg_ticket", 0)),
            top_customers=data.get("top_customers", [])[:5],
            overdue_receivables=float(data.get("overdue_receivables", 0)),
            dso_days=data.get("dso_days"),
        )

    def fetch_finance(self, on_date: date) -> FinanceKPIs:
        # TODO: endpoint real (muchos ERP comerciales exponen caja/margen aqui)
        data = self.client.get(
            "/reports/daily-finance",
            params={"date": on_date.isoformat()},
        )
        return FinanceKPIs(
            cash_balance=float(data.get("cash_balance", 0)),
            inflows_today=float(data.get("inflows_today", 0)),
            outflows_today=float(data.get("outflows_today", 0)),
            gross_margin_pct=data.get("gross_margin_pct"),
            opex_mtd=float(data.get("opex_mtd", 0)),
            opex_budget_mtd=float(data.get("opex_budget_mtd", 0)),
            anomalies=data.get("anomalies", []),
        )

    def close(self) -> None:
        self.client.close()
