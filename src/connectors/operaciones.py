from __future__ import annotations
from datetime import date
from .base import ERPClient
from ..models import InventoryKPIs, OperationsKPIs


class ErpOpsConnector:
    """
    Conector para operaciones.sekufoods.com (ERP de operaciones).
    Responsable de: inventario, compras, produccion, OTIF, mermas.

    NOTA: los paths son placeholders. Ajustar a la doc oficial del ERP.
    """

    def __init__(self, base_url: str, api_key: str):
        self.client = ERPClient(base_url, api_key)

    def fetch_inventory(self, on_date: date) -> InventoryKPIs:
        # TODO: endpoint real
        data = self.client.get(
            "/reports/daily-inventory",
            params={"date": on_date.isoformat()},
        )
        return InventoryKPIs(
            sku_below_min=data.get("sku_below_min", [])[:20],
            expiring_30d=data.get("expiring_30d", [])[:20],
            inventory_value=float(data.get("inventory_value", 0)),
            turnover_days=data.get("turnover_days"),
            open_purchase_orders=int(data.get("open_purchase_orders", 0)),
        )

    def fetch_operations(self, on_date: date) -> OperationsKPIs:
        # TODO: endpoint real
        data = self.client.get(
            "/reports/daily-production",
            params={"date": on_date.isoformat()},
        )
        plan = float(data.get("production_plan", 0))
        actual = float(data.get("production_actual", 0))
        compliance = (actual / plan * 100.0) if plan > 0 else None
        return OperationsKPIs(
            production_plan=plan,
            production_actual=actual,
            compliance_pct=compliance,
            scrap_pct=data.get("scrap_pct"),
            otif_pct=data.get("otif_pct"),
            line_downtime_min=float(data.get("line_downtime_min", 0)),
            incidents=data.get("incidents", [])[:10],
        )

    def close(self) -> None:
        self.client.close()
