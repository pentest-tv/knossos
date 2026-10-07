#!/bin/bash
# Inject the per-deploy vulnerability-scanning flag into the SNMP system description
# (sysDescr, OID .1.3.6.1.2.1.1.1.0), a classic over-shared field that a service scan
# reads straight out. Then run snmpd in the foreground. The flag comes from the shared
# svc_flags volume so it rotates per deploy.
set -e

FLAG="$(cat /svc/snmp_flag.txt 2>/dev/null || echo 'PENTESTTV{flag-not-planted}')"

# Re-read the flag on every start: strip any prior override line, then add the current
# one. This way restarting the container after a re-plant serves the CURRENT sysDescr
# flag instead of permanently baking in the first-deploy value. snmpd reads the default
# config file.
sed -i '/maint token/d' /etc/snmp/snmpd.conf 2>/dev/null || true
printf '\noverride .1.3.6.1.2.1.1.1.0 octet_str "Pentest.TV net-01 managed switch; maint token %s"\n' \
  "$FLAG" >> /etc/snmp/snmpd.conf

exec snmpd -f -Lo
