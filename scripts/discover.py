#!/usr/bin/env python3
"""
Descubre los endpoints de los dos ERP probando rutas comunes.
Corre esto en el VPS que esta en el allowlist:

    python3 scripts/discover.py > discovery.json

Luego comparte discovery.json para cablear los connectors reales.
"""
from __future__ import annotations
import json
import os
import sys
from dotenv import load_dotenv
import httpx

load_dotenv()

COMMON_PATHS = [
    "/",
    "/api",
    "/api/",
    "/api/v1",
    "/api/v1/",
    "/api/v2",
    "/api/docs",
    "/api/documentation",
    "/api-docs",
    "/docs",
    "/redoc",
    "/swagger",
    "/swagger.json",
    "/swagger-ui",
    "/swagger-ui.html",
    "/api/swagger.json",
    "/api/swagger.yaml",
    "/openapi.json",
    "/openapi.yaml",
    "/api/openapi.json",
    "/api/v1/openapi.json",
    "/graphql",
    "/api/graphql",
    "/api/health",
    "/api/ping",
    "/api/status",
    "/api/version",
    "/api/me",
    "/api/user/me",
    # recursos que esperamos en un ERP comercial
    "/api/sales",
    "/api/invoices",
    "/api/customers",
    "/api/products",
    "/api/orders",
    "/api/receivables",
    "/api/reports",
    "/api/reports/sales",
    "/api/reports/daily-sales",
    # recursos que esperamos en un ERP de operaciones
    "/api/inventory",
    "/api/stock",
    "/api/warehouses",
    "/api/production",
    "/api/production-orders",
    "/api/purchase-orders",
    "/api/suppliers",
    "/api/reports/inventory",
    "/api/reports/production",
]


def probe(base_url: str, api_key: str) -> list[dict]:
    base = base_url.rstrip("/")
    # quita el /api final si el usuario ya lo incluyo, para poder probar ambos
    root = base[:-4] if base.endswith("/api") else base
    results = []
    tried = set()
    with httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-API-Key": api_key,
            "Accept": "application/json",
            "User-Agent": "ceo-app-discovery/1.0",
        },
        timeout=15,
        verify=True,
        follow_redirects=False,
    ) as client:
        for path in COMMON_PATHS:
            url = f"{root}{path}"
            if url in tried:
                continue
            tried.add(url)
            try:
                r = client.get(url)
                ct = r.headers.get("content-type", "")
                body_preview = r.text[:400] if ct.startswith(("application/json", "text/", "application/xml")) else f"<{len(r.content)} bytes {ct}>"
                results.append({
                    "url": url,
                    "status": r.status_code,
                    "content_type": ct,
                    "len": len(r.content),
                    "preview": body_preview,
                })
            except Exception as e:
                results.append({"url": url, "error": type(e).__name__, "detail": str(e)[:200]})
    return results


def main() -> int:
    out = {}
    for label, base_env, key_env in [
        ("erpcom", "ERPCOM_BASE_URL", "ERPCOM_API_KEY"),
        ("erpops", "ERPOPS_BASE_URL", "ERPOPS_API_KEY"),
    ]:
        base = os.environ.get(base_env, "").strip()
        key = os.environ.get(key_env, "").strip()
        if not base or not key:
            out[label] = {"error": f"faltan {base_env} o {key_env} en .env"}
            continue
        out[label] = {
            "base_url": base,
            "results": probe(base, key),
        }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
