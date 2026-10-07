# Jump host bridging the internal network to a restricted segment (enterprise
# segmentation). The student reaches it with the opsadmin credential leaked elsewhere
# (LDAP / wiki), then uses it to pivot a second time to the restricted vault host, which
# is not reachable from the attacker box directly. A note in opsadmin's home points at
# the vault credentials.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && useradd -m -s /bin/bash opsadmin \
    && echo 'opsadmin:OpsTransit#2024' | chpasswd \
    && printf 'Ops handover notes\n\nRestricted segment access:\n  vault host : vault-01.pentesttv.local (172.28.30.20)\n  account    : svc_vault\n  password   : V@ultKeeper2024\n\nReach it from this jump box only; it is firewalled off from the user LAN.\n' \
        > /home/opsadmin/handover-notes.txt \
    && chown opsadmin:opsadmin /home/opsadmin/handover-notes.txt \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
