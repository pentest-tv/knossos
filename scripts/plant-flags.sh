#!/usr/bin/env bash
# Runs inside the flag-init container during 'docker compose up'. Generates per-deploy
# flags, writes them into the target volumes, and records the lab flags for the
# platform. No student interaction. Volumes: /t -> target /root/ctf, /p -> pivot loot.
set -euo pipefail

PREFIX="${FLAG_PREFIX:-PENTESTTV}"
gen() { echo "${PREFIX}{$(head -c16 /dev/urandom | od -An -tx1 | tr -d ' \n')}"; }

WALK_FLAG="$(gen)"
LAB_FLAG="$(gen)"
PW_FLAG="$(gen)"
C2_FLAG="$(gen)"
EXFIL_FLAG="$(gen)"
DNS_FLAG="$(gen)"
MYSQL_FLAG="$(gen)"
PG_FLAG="$(gen)"
VNC_FLAG="$(gen)"
SMTP_FLAG="$(gen)"
PWCRACK_FLAG="$(gen)"
PILLAGE_FLAG="$(gen)"
CREDREUSE_FLAG="$(gen)"
MSF_FLAG="$(gen)"
SLIVER_FLAG="$(gen)"
SNMP_FLAG="$(gen)"
SUID_FLAG="$(gen)"
SUDO_FLAG="$(gen)"
SPRAY_FLAG="$(gen)"
WEBDISC_FLAG="$(gen)"
# Wireless PSK is baked into the shipped handshake capture, so this flag is static: it is
# the passphrase students recover by cracking wpa-handshake.pcap.
WIFI_FLAG="Baseball1"
# Enterprise per-deploy flags.
JWT_FLAG="$(gen)"
SYSLOG_FLAG="$(gen)"
VAULT_FLAG="$(gen)"
# Enterprise static flags (baked into the LDAP directory, git history, wiki page, and the
# shipped Kerberos ticket respectively; recorded here so the scoreboard can validate them).
LDAP_FLAG="PENTESTTV{ldap_anon_bind_leaks_service_creds}"
GIT_FLAG="PENTESTTV{secrets_live_forever_in_git_history}"
WIKI_FLAG="PENTESTTV{wiki_pages_leak_operational_creds}"
KRB_FLAG="Winter2024"

# Exploitation module: walkthrough (vsftpd) and graded lab (Samba), both on the Linux box.
printf '%s\n' "$WALK_FLAG" > /t/walkthrough_flag.txt
printf '%s\n' "$LAB_FLAG"  > /t/lab_flag.txt
chmod 644 /t/walkthrough_flag.txt /t/lab_flag.txt

# Password-attack module: flag in jsmith's home, readable only after a successful SSH
# login, so recovering the password by brute force is required to claim it.
printf '%s\n' "$PW_FLAG" > /p/pwattack_flag.txt
chmod 644 /p/pwattack_flag.txt

# C2 module: flag on the internal pivot host.
printf '%s\n' "$C2_FLAG" > /p/c2_flag.txt
chmod 644 /p/c2_flag.txt

# Actions on objectives: exfil flag on the crown-jewel file server share.
printf '%s\n' "$EXFIL_FLAG" > /x/exfil_flag.txt
chmod 644 /x/exfil_flag.txt

# Pillaging module: an application config left on the perimeter target. It carries the
# build-token flag plus a service account's credentials that are reused elsewhere.
cat > /t/app_config.php <<PHP
<?php
// Pentest.TV internal application config. DO NOT COMMIT.
\$DB_HOST = '172.28.20.60';
\$DB_NAME = 'corp';
\$DB_USER = 'svcapp';
\$DB_PASS = 'Falcon2023!';
// Ops note: svcapp reuses this password for SSH on the internal workstation hosts.
// build token (internal): ${PILLAGE_FLAG}
PHP
chmod 644 /t/app_config.php

# Credential-reuse module: flag in svcapp's home on the pivot (/ps -> /home/svcapp/loot),
# reachable once the student logs in with the looted svcapp credentials.
printf '%s\n' "$CREDREUSE_FLAG" > /ps/credreuse_flag.txt
chmod 644 /ps/credreuse_flag.txt

# Payload-delivery and C2 modules: flags in the workstation victim's home
# (/pw -> ws-03 /home/victim/loot), readable once a payload or implant gives a session.
printf '%s\n' "$MSF_FLAG"    > /pw/user_flag.txt
printf '%s\n' "$SLIVER_FLAG" > /pw/c2_flag.txt
chmod 644 /pw/user_flag.txt /pw/c2_flag.txt

# SUID and sudo privilege-escalation modules: root-only flags on the workstation
# (/wsr -> ws-03 /root/ctf), readable only after the victim foothold escalates to root.
printf '%s\n' "$SUID_FLAG" > /wsr/suid_flag.txt
printf '%s\n' "$SUDO_FLAG" > /wsr/sudo_flag.txt
chmod 600 /wsr/suid_flag.txt /wsr/sudo_flag.txt

# Password-spraying module: flag in pmorgan's home on the pivot (/spray -> /home/pmorgan/loot),
# reachable once a spray lands on that reused seasonal password.
printf '%s\n' "$SPRAY_FLAG" > /spray/spray_flag.txt
chmod 644 /spray/spray_flag.txt

# Web content-discovery module: flag in the intranet server's hidden /backup directory
# (/webroot -> web-03 /srv/www/backup), found by directory brute forcing.
printf '%s\n' "$WEBDISC_FLAG" > /webroot/flag.txt
chmod 644 /webroot/flag.txt

# SSO/JWT module: flag served by the admin endpoint, read from the shared svc_flags volume.
printf '%s\n' "$JWT_FLAG" > /svc/jwt_flag.txt
chmod 644 /svc/jwt_flag.txt

# Restricted-segment vault flag (/vault -> vault-01 /home/svc_vault/loot), reachable only
# by double-pivoting through the jump host.
printf '%s\n' "$VAULT_FLAG" > /vault/vault_flag.txt
chmod 644 /vault/vault_flag.txt

# Central log server: an application log that leaks a database credential in cleartext and
# carries the audit flag (/logs -> log-01 /srv/export).
cat > /logs/app.log <<LOG
$(date -u '+%Y-%m-%dT%H:%M:%SZ') app[1123]: starting reporting worker, env=prod
$(date -u '+%Y-%m-%dT%H:%M:%SZ') app[1123]: INFO connecting to db-01.pentesttv.local:5432
$(date -u '+%Y-%m-%dT%H:%M:%SZ') app[1123]: WARN config loaded with DB_USER=reporting DB_PASS=Rep0rting#2024 (remove debug logging before prod)
$(date -u '+%Y-%m-%dT%H:%M:%SZ') app[1123]: INFO reporting job complete, 48213 rows
$(date -u '+%Y-%m-%dT%H:%M:%SZ') audit[9]: nightly integrity token ${SYSLOG_FLAG}
$(date -u '+%Y-%m-%dT%H:%M:%SZ') sshd[204]: Accepted password for opsadmin from 172.28.20.100
LOG
chmod 644 /logs/app.log

# Local privilege-escalation module: root-only flag on the pivot (/pr -> pivot /root/ctf).
# Mode 600 and owned by root, so the jsmith foothold cannot read it until it cracks
# root's password and su's to root.
printf '%s\n' "$PWCRACK_FLAG" > /pr/pwcrack_flag.txt
chmod 600 /pr/pwcrack_flag.txt

# Service exploitation modules: per-deploy flags the DB and VNC targets read at startup
# from the shared svc_flags volume (/svc).
printf '%s\n' "$MYSQL_FLAG" > /svc/mysql_flag.txt
printf '%s\n' "$PG_FLAG"    > /svc/pg_flag.txt
printf '%s\n' "$VNC_FLAG"   > /svc/vnc_flag.txt
printf '%s\n' "$SMTP_FLAG"  > /svc/smtp_flag.txt
printf '%s\n' "$SNMP_FLAG"  > /svc/snmp_flag.txt
chmod 644 /svc/mysql_flag.txt /svc/pg_flag.txt /svc/vnc_flag.txt /svc/smtp_flag.txt /svc/snmp_flag.txt

# Reconnaissance: write the DNS zone with the flag as a TXT record, revealed only by a
# zone transfer (AXFR). /z is the shared volume the bind server reads at /zones.
SERIAL="$(date +%s)"
cat > /z/db.pentesttv.local <<ZONE
\$TTL 3600
@         IN SOA dns-01.pentesttv.local. admin.pentesttv.local. ( ${SERIAL} 3600 600 86400 3600 )
@         IN NS  dns-01.pentesttv.local.
dns-01    IN A   172.28.10.34
dmz-01    IN A   172.28.10.20
web-01    IN A   172.28.10.30
web-02    IN A   172.28.10.31
web-03    IN A   172.28.20.130
phish-01  IN A   172.28.10.32
mail-01   IN A   172.28.10.33
db-01     IN A   172.28.10.40
db-02     IN A   172.28.10.41
vnc-01    IN A   172.28.10.42
smtp-01   IN A   172.28.10.43
c2-01     IN A   172.28.10.50
net-01    IN A   172.28.20.40
ws-03     IN A   172.28.20.70
ws-01     IN A   172.28.20.50
files-01  IN A   172.28.20.60
ws-02     IN A   172.28.20.61
ldap-01   IN A   172.28.20.90
jump-01   IN A   172.28.20.100
log-01    IN A   172.28.20.110
print-01  IN A   172.28.20.120
git-01    IN A   172.28.20.131
wiki-01   IN A   172.28.20.132
sso-01    IN A   172.28.10.72
hr-app-01 IN A   172.28.10.73
vault-01  IN A   172.28.30.20
attacker  IN A   172.28.10.10
flag      IN TXT "${DNS_FLAG}"
; Wildcard under exfil.pentesttv.local resolves any label, so DNS-exfil queries get an
; answer instead of NXDOMAIN. This is the channel the data-exfiltration module uses.
*.exfil   IN A   127.0.0.1
ZONE
chmod 644 /z/db.pentesttv.local

# Record for the platform validator. Not committed (see .gitignore).
FLAGS_BODY="# Generated at deploy $(date -u +%FT%TZ). Load into the platform; do not commit.
MODULE_04_DNS_FLAG=${DNS_FLAG}
MODULE_07_WALKTHROUGH_FLAG=${WALK_FLAG}
MODULE_07_LAB_FLAG=${LAB_FLAG}
MODULE_07B_PW_FLAG=${PW_FLAG}
MODULE_09_C2_FLAG=${C2_FLAG}
MODULE_10_EXFIL_FLAG=${EXFIL_FLAG}
MODULE_07C_MYSQL_FLAG=${MYSQL_FLAG}
MODULE_07D_PG_FLAG=${PG_FLAG}
MODULE_07E_VNC_FLAG=${VNC_FLAG}
MODULE_07F_SMTP_FLAG=${SMTP_FLAG}
MODULE_11B_PWCRACK_FLAG=${PWCRACK_FLAG}
MODULE_12A_PILLAGE_FLAG=${PILLAGE_FLAG}
MODULE_12B_CREDREUSE_FLAG=${CREDREUSE_FLAG}
MODULE_08A_MSF_FLAG=${MSF_FLAG}
MODULE_09D_SLIVER_FLAG=${SLIVER_FLAG}
MODULE_04B_VULNSCAN_FLAG=${SNMP_FLAG}
MODULE_11C_SUID_FLAG=${SUID_FLAG}
MODULE_11D_SUDO_FLAG=${SUDO_FLAG}
MODULE_07G_SPRAY_FLAG=${SPRAY_FLAG}
MODULE_06C_WEBDISC_FLAG=${WEBDISC_FLAG}
MODULE_13_WIFI_FLAG=${WIFI_FLAG}
MODULE_ENT_LDAP_FLAG=${LDAP_FLAG}
MODULE_ENT_GIT_FLAG=${GIT_FLAG}
MODULE_ENT_WIKI_FLAG=${WIKI_FLAG}
MODULE_ENT_JWT_FLAG=${JWT_FLAG}
MODULE_ENT_SYSLOG_FLAG=${SYSLOG_FLAG}
MODULE_ENT_VAULT_FLAG=${VAULT_FLAG}
MODULE_ENT_KRB_FLAG=${KRB_FLAG}"

# Host copy (for you) and shared-volume copy (for the scoreboard container).
printf '%s\n' "$FLAGS_BODY" > /out/flags.generated.env
printf '%s\n' "$FLAGS_BODY" > /sb/flags.env

echo "flag-init: flags planted and recorded in flags.generated.env"
