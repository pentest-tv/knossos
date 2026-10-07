# Internal workstation (ws-03) for payload delivery and post-exploitation (book ch 7-8,
# 11-12). It exposes a world-writable SMB share called "drop" and runs a loop that
# executes whatever lands there as the low-privilege user "victim", simulating a user who
# opens a malicious attachment. A payload that calls back (msfvenom meterpreter or a Sliver
# implant) gives the student a session as victim, whose home holds the module flags.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends samba procps sudo findutils \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash victim \
    && mkdir -p /srv/drop/done /home/victim/loot /root/ctf \
    && chmod 1777 /srv/drop \
    # SUID privilege-escalation path: a setuid-root copy of a shell, found with
    # `find / -perm -4000` and abused with `backuptool -p` to get an euid-0 shell.
    && cp /bin/bash /usr/bin/backuptool \
    && chmod 4755 /usr/bin/backuptool \
    # sudo privilege-escalation path: victim may run find as root with no password,
    # which GTFOBins turns into a root shell (sudo find . -exec /bin/sh \; -quit).
    && echo 'victim ALL=(ALL) NOPASSWD: /usr/bin/find' > /etc/sudoers.d/victim \
    && chmod 440 /etc/sudoers.d/victim

COPY smb.conf /etc/samba/smb.conf
COPY runner.sh /usr/local/bin/runner.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/runner.sh /usr/local/bin/entrypoint.sh

EXPOSE 139 445
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
