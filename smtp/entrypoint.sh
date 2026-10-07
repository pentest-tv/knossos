#!/bin/bash
# Set the per-deploy flag into the SMTP banner (read from the shared svc_flags volume),
# then start Postfix in the foreground as PID 1. The banner leak is the finding: a
# student who grabs the SMTP banner during enumeration captures the flag. The banner
# still begins with $myhostname, as Postfix requires.
set -e

FLAG="$(cat /svc/smtp_flag.txt 2>/dev/null || echo 'PENTESTTV{flag-not-planted}')"
postconf -e "smtpd_banner = \$myhostname ESMTP Pentest.TV mail relay (maint-note ${FLAG})"

newaliases 2>/dev/null || true
exec /usr/sbin/postfix start-fg
