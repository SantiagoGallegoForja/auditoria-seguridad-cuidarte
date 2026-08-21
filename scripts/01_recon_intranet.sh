#!/bin/bash
# =============================================================================
# RECONOCIMIENTO COMPLETO DE INTRANET - Cuidarte Tu Salud
# Auditoria Autorizada - Equipo de Ciberseguridad
# Fecha: 2026-04-16
# =============================================================================

TARGET_IP="190.66.24.91"
HIS_PORT="3155"
KACTUS_PORT="3151"
HIS_BASE="http://${TARGET_IP}:${HIS_PORT}"
KACTUS_BASE="http://${TARGET_IP}:${KACTUS_PORT}"
OUT_DIR="./recon_output"
mkdir -p "$OUT_DIR"

echo "============================================"
echo " FASE 1: RECONOCIMIENTO DE PUERTOS"
echo "============================================"

# Escaneo de puertos conocidos + AJP (GhostCat)
echo "[*] Escaneando puertos del objetivo..."
nmap -sV -sC -p 3155,3151,8009,8080,443,80,22,3389,1433,3306,5432 "$TARGET_IP" -oN "$OUT_DIR/nmap_targeted.txt" 2>/dev/null
echo "[+] Resultado en $OUT_DIR/nmap_targeted.txt"

# Escaneo completo de puertos (background, toma tiempo)
echo "[*] Iniciando escaneo completo de puertos (background)..."
nmap -sV -p- --min-rate 1000 "$TARGET_IP" -oN "$OUT_DIR/nmap_full.txt" 2>/dev/null &
NMAP_PID=$!
echo "[+] PID: $NMAP_PID - resultado en $OUT_DIR/nmap_full.txt"

echo ""
echo "============================================"
echo " FASE 2: FINGERPRINTING HIS (TOMCAT)"
echo "============================================"

echo "[*] Headers del login HIS..."
curl -sk -D "$OUT_DIR/his_headers.txt" -o "$OUT_DIR/his_login.html" \
  --max-time 15 "${HIS_BASE}/WEBHOSREAL/servlet/login"
echo "[+] Headers guardados en $OUT_DIR/his_headers.txt"

echo "[*] Pagina root de Tomcat..."
curl -sk -o "$OUT_DIR/tomcat_root.html" --max-time 10 "${HIS_BASE}/"

echo "[*] Tomcat Manager..."
curl -sk -D "$OUT_DIR/tomcat_manager_headers.txt" -o /dev/null \
  --max-time 10 "${HIS_BASE}/manager/html"

echo "[*] Tomcat Host Manager..."
curl -sk -D "$OUT_DIR/tomcat_hostmgr_headers.txt" -o /dev/null \
  --max-time 10 "${HIS_BASE}/host-manager/html"

echo "[*] Documentacion Tomcat..."
curl -sk -D "$OUT_DIR/tomcat_docs_headers.txt" -o "$OUT_DIR/tomcat_docs.html" \
  --max-time 10 "${HIS_BASE}/docs/"

echo "[*] Servlets del HIS..."
for SERVLET in login home hadmision henfermeria hordmed hcitas hurgencias hlaboratorio; do
  CODE=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 \
    "${HIS_BASE}/WEBHOSREAL/servlet/${SERVLET}")
  echo "  /servlet/${SERVLET} => HTTP $CODE"
done | tee "$OUT_DIR/servlets_scan.txt"

echo ""
echo "============================================"
echo " FASE 3: JAVASCRIPT EXPUESTO (SIN AUTH)"
echo "============================================"

echo "[*] Descargando JS de modulos clinicos..."
for JS in login.js home.js hadmision.js hordmed.js henfermeria.js gxgral.js gxcfg.js; do
  SIZE=$(curl -sk -o "$OUT_DIR/${JS}" -w "%{size_download}" \
    --max-time 30 "${HIS_BASE}/WEBHOSREAL/static/${JS}")
  echo "  ${JS} => ${SIZE} bytes"
done | tee "$OUT_DIR/js_download.txt"

echo ""
echo "============================================"
echo " FASE 4: FINGERPRINTING KACTUS (IIS)"
echo "============================================"

echo "[*] Headers del login KACTUS..."
curl -sk -D "$OUT_DIR/kactus_headers.txt" -o "$OUT_DIR/kactus_login.html" \
  --max-time 15 "${KACTUS_BASE}/frmLogin.aspx"
echo "[+] Headers guardados"

echo "[*] Directorios de KACTUS..."
for DIR in DwCss DwCss/DwLogin assets assets/js assets/css DwImg DwImg/imgLogos Banner; do
  CODE=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 \
    "${KACTUS_BASE}/${DIR}/")
  echo "  /${DIR}/ => HTTP $CODE"
done | tee "$OUT_DIR/kactus_dirs.txt"

echo "[*] Endpoints KACTUS adicionales..."
for PAGE in default.aspx frmCerrar.aspx frmLoginAzure.aspx; do
  CODE=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 \
    "${KACTUS_BASE}/${PAGE}")
  echo "  /${PAGE} => HTTP $CODE"
done | tee "$OUT_DIR/kactus_endpoints.txt"

echo ""
echo "============================================"
echo " FASE 5: SISTEMAS EXTERNOS"
echo "============================================"

echo "[*] SGI Almera..."
curl -sk -D "$OUT_DIR/sgi_headers.txt" -o /dev/null --max-time 10 \
  "https://sgi.almeraim.com/sgi/index.php?conid=sgicuidartetusalud"

echo "[*] ZonaPagos..."
curl -sk -D "$OUT_DIR/zonapagos_headers.txt" -o /dev/null --max-time 10 \
  "https://www.zonapagos.com/t_tusalud/pagos.asp"

echo "[*] Mangus (educativa)..."
curl -sk -D "$OUT_DIR/mangus_headers.txt" -o /dev/null --max-time 10 \
  "https://cuidateeduca.mangus.co/"

echo "[*] Glya COVID..."
curl -sk -D "$OUT_DIR/glya_headers.txt" -o /dev/null --max-time 10 \
  "https://cuidartecovid.glya.co/practitioners/sign_in"

echo ""
echo "============================================"
echo " FASE 6: NIKTO / NUCLEI (si disponibles)"
echo "============================================"

if command -v nikto &>/dev/null; then
  echo "[*] Nikto contra HIS..."
  nikto -h "${HIS_BASE}/WEBHOSREAL/" -o "$OUT_DIR/nikto_his.txt" &
  echo "[*] Nikto contra KACTUS..."
  nikto -h "${KACTUS_BASE}" -o "$OUT_DIR/nikto_kactus.txt" &
else
  echo "[-] nikto no encontrado. Instalar: apt install nikto"
fi

if command -v nuclei &>/dev/null; then
  echo "[*] Nuclei contra HIS..."
  nuclei -u "${HIS_BASE}" -o "$OUT_DIR/nuclei_his.txt" &
  echo "[*] Nuclei contra KACTUS..."
  nuclei -u "${KACTUS_BASE}" -o "$OUT_DIR/nuclei_kactus.txt" &
else
  echo "[-] nuclei no encontrado. Instalar: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
fi

echo ""
echo "============================================"
echo " RECON COMPLETO"
echo "============================================"
echo "[+] Todos los resultados en: $OUT_DIR/"
ls -la "$OUT_DIR/"
