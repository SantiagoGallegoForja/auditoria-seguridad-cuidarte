#!/usr/bin/env python3
"""
EXTRACCION DE CAMPOS DE DATOS - JavaScript del HIS
Auditoria Autorizada - Cuidarte Tu Salud

Descarga y analiza los JS expuestos del HIS para extraer:
- Campos de datos de pacientes
- Endpoints/servlets internos
- Variables de configuracion
- Estructura de la base de datos

Uso:
  python3 04_extract_js_fields.py
"""

import requests
import re
import json
import os

BASE = "http://190.66.24.91:3155/WEBHOSREAL/static"
OUT_DIR = "./js_analysis"
os.makedirs(OUT_DIR, exist_ok=True)

JS_FILES = {
    "login.js": "Login - Autenticacion",
    "home.js": "Home - Pagina principal",
    "hadmision.js": "Admisiones - Datos de pacientes",
    "hordmed.js": "Ordenes Medicas - Diagnosticos y procedimientos",
    "henfermeria.js": "Enfermeria - Triage y seguimiento",
    "gxgral.js": "GeneXus Framework - Core",
    "gxcfg.js": "GeneXus Config",
}

# Patrones sensibles a buscar
SENSITIVE_PATTERNS = {
    "campos_formulario": r'fld:"([^"]+)"',
    "variables_gx": r'gxvar:"([^"]+)"',
    "servlets_url": r'servlet/(\w+)',
    "eventos_servidor": r'executeServerEvent\("([^"]+)"',
    "tipos_datos": r'type:"(\w+)"',
    "longitudes": r'len:(\d+)',
    "ajax_calls": r'gx\.ajax\.\w+\([^)]*"([^"]*)"',
    "urls_internas": r'(?:href|src|action|url)\s*[=:]\s*["\']([^"\']+)["\']',
    "tokens_security": r'(?:SECURITY|TOKEN|SESSION|KEY)["\']?\s*[=:]\s*["\']([^"\']+)',
    "sql_fragments": r'(?:SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN)\s+\w+',
}

# Campos conocidos sensibles (para clasificacion)
SENSITIVE_FIELD_KEYWORDS = {
    "CRITICO": ["CEDU", "NOMI", "DIRE", "TELE", "FCHN", "DIAGN", "HIST", "OBSER",
                 "CEDULA", "NOMBRE", "DIRECCION", "TELEFONO", "NACIMIENTO"],
    "ALTO": ["SEXO", "EDAD", "MEDICO", "ESPEC", "FOLIO", "CITNUM", "CONTRATO",
             "FACTURA", "DXPP", "PRIORI", "SEVER"],
    "MEDIO": ["SEDE", "PABELL", "CAMA", "MODULO", "SERVICIO", "ESTADO"],
}


def download_js(filename):
    """Descarga un archivo JS del HIS."""
    url = f"{BASE}/{filename}"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            filepath = os.path.join(OUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(r.text)
            return r.text
        else:
            print(f"  [-] {filename}: HTTP {r.status_code}")
            return None
    except Exception as e:
        print(f"  [-] {filename}: {e}")
        return None


def classify_field(field_name):
    """Clasifica un campo por nivel de sensibilidad."""
    upper = field_name.upper()
    for level, keywords in SENSITIVE_FIELD_KEYWORDS.items():
        if any(kw in upper for kw in keywords):
            return level
    return "INFO"


def analyze_js(content, filename):
    """Analiza un JS y extrae campos, endpoints, etc."""
    results = {}
    for pattern_name, regex in SENSITIVE_PATTERNS.items():
        matches = re.findall(regex, content, re.IGNORECASE)
        if matches:
            results[pattern_name] = list(set(matches))
    return results


def main():
    print("=" * 80)
    print(" ANALISIS DE JAVASCRIPT EXPUESTO - HosVital HIS")
    print(" Sin autenticacion - accesible publicamente")
    print("=" * 80)

    all_results = {}
    all_fields = []

    for filename, description in JS_FILES.items():
        print(f"\n[*] {filename} ({description})...")
        content = download_js(filename)
        if not content:
            continue

        size_kb = len(content) / 1024
        print(f"  [+] Descargado: {size_kb:.1f} KB")

        analysis = analyze_js(content, filename)
        all_results[filename] = analysis

        if "campos_formulario" in analysis:
            fields = analysis["campos_formulario"]
            print(f"  [+] Campos encontrados: {len(fields)}")

            for field in sorted(fields):
                level = classify_field(field)
                if level in ("CRITICO", "ALTO"):
                    print(f"    [{level}] {field}")
                all_fields.append({"file": filename, "field": field, "level": level})

        if "eventos_servidor" in analysis:
            print(f"  [+] Eventos servidor: {len(analysis['eventos_servidor'])}")
            for evt in sorted(analysis["eventos_servidor"]):
                print(f"    -> {evt}")

        if "servlets_url" in analysis:
            print(f"  [+] Servlets referenciados: {analysis['servlets_url']}")

    # Resumen
    print("\n" + "=" * 80)
    print(" RESUMEN")
    print("=" * 80)

    total_fields = len(all_fields)
    criticos = [f for f in all_fields if f["level"] == "CRITICO"]
    altos = [f for f in all_fields if f["level"] == "ALTO"]

    print(f"\n[+] Total campos expuestos: {total_fields}")
    print(f"[+] Campos CRITICOS: {len(criticos)}")
    print(f"[+] Campos ALTOS: {len(altos)}")

    if criticos:
        print("\n CAMPOS CRITICOS (datos personales de pacientes):")
        for f in criticos:
            print(f"   [{f['file']}] {f['field']}")

    # Guardar resultados
    report_path = os.path.join(OUT_DIR, "analysis_report.json")
    with open(report_path, "w") as f:
        json.dump({
            "target": BASE,
            "total_fields": total_fields,
            "critical_fields": len(criticos),
            "high_fields": len(altos),
            "fields": all_fields,
            "analysis": {k: {pk: pv for pk, pv in v.items()} for k, v in all_results.items()},
        }, f, indent=2)

    print(f"\n[+] Reporte completo en: {report_path}")
    print(f"[+] JS descargados en: {OUT_DIR}/")


if __name__ == "__main__":
    main()
