# SMTP target for the mail-server enumeration module (book ch 9, SMTP). A Postfix
# instance that is deliberately misconfigured as an open relay and still answers the
# VRFY command, so the student can enumerate valid local users (including jsmith, a
# fourth way to recover that username) and demonstrate the open relay. Base image
# pinned by digest via BASE_DEBIAN.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends postfix rsyslog \
    && rm -rf /var/lib/apt/lists/* \
    # Local users an attacker can confirm with SMTP VRFY. jsmith is the real account;
    # the others are decoys so enumeration is a real exercise, not a single guess.
    && useradd -m jsmith \
    && useradd -m ahill \
    && useradd -m mkhan \
    && useradd -m svc-backup \
    && postconf -e "myhostname = smtp-01.pentesttv.local" \
    && postconf -e "mydestination = smtp-01.pentesttv.local, localhost" \
    && postconf -e "inet_interfaces = all" \
    && postconf -e "inet_protocols = ipv4" \
    # Deliberate misconfigurations the module teaches:
    && postconf -e "mynetworks = 0.0.0.0/0" \
    && postconf -e "disable_vrfy_command = no" \
    # Relax modern anti-pipelining and bare-newline enforcement so simple enumeration
    # (piped VRFY, smtp-user-enum, hand-typed nc) works against this intentionally
    # permissive target instead of being rejected with a protocol-synchronization error.
    && postconf -e "smtpd_forbid_unauth_pipelining = no" \
    && postconf -e "smtpd_forbid_bare_newline = no" \
    && postconf -e "smtpd_banner = \$myhostname ESMTP Pentest.TV mail relay" \
    && newaliases

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 25
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
