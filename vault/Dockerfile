# Restricted-segment crown jewel (vault-01). It lives only on the restricted network, so
# the attacker box cannot reach it directly: the student must pivot through the jump host
# with the svc_vault credential found there. The final flag is in svc_vault's loot.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && useradd -m -s /bin/bash svc_vault \
    && echo 'svc_vault:V@ultKeeper2024' | chpasswd \
    && mkdir -p /home/svc_vault/loot \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
