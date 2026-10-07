# Internal pivot host. It carries several modules:
#  - Password Attack (ch 9): jsmith has a weak SSH password recovered by remote brute force.
#  - Command and Control (ch 11) and Installation/Persistence (ch 10) build on that login.
#  - Local Password Attack + Privilege Escalation (ch 11): a world-readable /etc/shadow
#    backup lets the jsmith foothold crack root's password offline and su to root.
# sshd on this host is tuned to survive the intended brute-force/spray: MaxStartups and
# LoginGraceTime are raised/shortened below so the attack does not trip sshd's defaults
# and reset the logins students just recovered.
# cron is installed so userland persistence (cron jobs, ssh keys, .bashrc) works.
# Base image is pinned by digest via the BASE_DEBIAN build arg.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server cron \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd /root/ctf \
    && useradd -m -s /bin/bash jsmith \
    && echo 'jsmith:Password1' | chpasswd \
    # svcapp is a service account whose password is reused (and leaked in a config the
    # student pillages from the perimeter host). Logging in here with those looted creds
    # is the credential-reuse / lateral-movement module.
    && useradd -m -s /bin/bash svcapp \
    && echo 'svcapp:Falcon2023!' | chpasswd \
    && mkdir -p /home/svcapp/loot \
    # Password-spraying target set. Most of these accounts have no usable password
    # (locked), but pmorgan reused the company's seasonal password, so spraying one
    # common password across the user list lands on that account.
    && useradd -m -s /bin/bash rturner \
    && useradd -m -s /bin/bash lchen \
    && useradd -m -s /bin/bash dwood \
    && useradd -m -s /bin/bash ksingh \
    && useradd -m -s /bin/bash pmorgan \
    && echo 'pmorgan:Autumn2024' | chpasswd \
    && mkdir -p /home/pmorgan/loot \
    # root has a weak, crackable password too. A world-readable backup of /etc/shadow
    # (a classic operational mistake) lets the jsmith foothold read root's hash, crack
    # it offline, and su to root: the local password attack + privilege escalation.
    && echo 'root:Summer2024' | chpasswd \
    && cp /etc/shadow /var/backups/shadow.bak \
    && chmod 644 /var/backups/shadow.bak \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && printf 'MaxStartups 100:30:200\nLoginGraceTime 30\n' >> /etc/ssh/sshd_config

EXPOSE 22
# Start cron in the background, then sshd in the foreground as PID 1.
CMD ["/bin/sh", "-c", "cron && exec /usr/sbin/sshd -D -e"]
