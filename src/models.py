from __future__ import annotations
from datetime import date
from typing import Any
from pydantic import BaseModel, Field


class SalesKPIs(BaseModel):
    revenue_today: float = 0.0
    revenue_mtd: float = 0.0
    revenue_goal_mtd: float = 0.0
    orders_count: int = 0
    avg_ticket: float = 0.0
    top_customers: list[dict[str, Any]] = Field(default_factory=list)
    overdue_receivables: float = 0.0
    dso_days: float | None = None


class InventoryKPIs(BaseModel):
    sku_below_min: list[dict[str, Any]] = Field(default_factory=list)
    expiring_30d: list[dict[str, Any]] = Field(default_factory=list)
    inventory_value: float = 0.0
    turnover_days: float | None = None
    open_purchase_orders: int = 0


class OperationsKPIs(BaseModel):
    production_plan: float = 0.0
    production_actual: float = 0.0
    compliance_pct: float | None = None
    scrap_pct: float | None = None
    otif_pct: float | None = None
    line_downtime_min: float = 0.0
    incidents: list[dict[str, Any]] = Field(default_factory=list)


class FinanceKPIs(BaseModel):
    cash_balance: float = 0.0
    inflows_today: float = 0.0
    outflows_today: float = 0.0
    gross_margin_pct: float | None = None
    opex_mtd: float = 0.0
    opex_budget_mtd: float = 0.0
    anomalies: list[dict[str, Any]] = Field(default_factory=list)


class DailyBrief(BaseModel):
    brief_date: date
    sales: SalesKPIs = Field(default_factory=SalesKPIs)
    inventory: InventoryKPIs = Field(default_factory=InventoryKPIs)
    operations: OperationsKPIs = Field(default_factory=OperationsKPIs)
    finance: FinanceKPIs = Field(default_factory=FinanceKPIs)
    raw: dict[str, Any] = Field(default_factory=dict)


class CEOInsight(BaseModel):
    severity: str  # "critico" | "alto" | "medio" | "informativo"
    area: str
    titulo: str
    hallazgo: str
    recomendacion: str
    accion_inmediata: str | None = None


class CEOReport(BaseModel):
    brief_date: date
    resumen_ejecutivo: str
    semaforo: str  # "verde" | "amarillo" | "rojo"
    insights: list[CEOInsight]
    metricas_clave: dict[str, Any] = Field(default_factory=dict)
