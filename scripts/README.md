# Scripts de Pentesting - Cuidarte Tu Salud
## Auditoria Autorizada - 2026-04-16

### Orden de ejecucion recomendado

| # | Script | Descripcion | Requisitos |
|---|--------|-------------|------------|
| 01 | `01_recon_intranet.sh` | Reconocimiento completo de la IP y sistemas | nmap, curl, nikto (opc), nuclei (opc) |
| 02 | `02_enum_users.py` | Enumeracion de usuarios validos en HIS | Python 3 + requests |
| 03 | `03_brute_his.py` | Brute force al login del HIS | Python 3 + requests |
| 04 | `04_extract_js_fields.py` | Descarga y analiza JS expuestos | Python 3 + requests |
| 05 | `05_test_sqli.py` | Pruebas de SQL Injection en login | Python 3 + requests |
| 06 | `06_ghostcat_check.sh` | Verifica CVE-2020-1938 (GhostCat/AJP) | nmap, ajpShooter (opc) |
| 07 | `07_wix_token_steal.py` | Exfiltracion de tokens via CORS | Python 3 + requests |

### Instalacion de dependencias

```bash
pip install requests
```

### Uso rapido

```bash
# 1. Reconocimiento
chmod +x 01_recon_intranet.sh && ./01_recon_intranet.sh

# 2. Enumerar usuarios
python3 02_enum_users.py

# 3. Brute force con usuarios encontrados
python3 03_brute_his.py -u PRUEBA -d 0.5

# 4. Analizar JS
python3 04_extract_js_fields.py

# 5. SQLi
python3 05_test_sqli.py -v

# 6. GhostCat
chmod +x 06_ghostcat_check.sh && ./06_ghostcat_check.sh

# 7. Tokens Wix
python3 07_wix_token_steal.py
```

### Datos del objetivo

- **IP:** 190.66.24.91
- **HIS (Tomcat):** Puerto 3155 - HTTP (sin HTTPS)
- **KACTUS (IIS):** Puerto 3151 - HTTP (sin HTTPS)
- **Usuarios confirmados:** PRUEBA, hosvital
- **Sedes:** BOSQUE, CENTRO DE EXCELENCIA, ARMENIA, PEREIRA
- **Tomcat:** 6.0.53 (EOL) - Manager expuesto en /manager/html
- **Framework:** GeneXus Java v10.1.7
