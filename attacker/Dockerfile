# Optional browser-accessible Kali attacker. Serves a terminal at :7681 via ttyd so a
# student can work the lab with only Docker and a browser. Base image is pinned by
# digest via the BASE_KALI build arg.
ARG BASE_KALI=kalilinux/kali-rolling:latest
FROM ${BASE_KALI}

ARG SLIVER_VERSION=v1.5.43
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        kali-linux-headless ttyd iproute2 iputils-ping hydra wordlists \
        default-mysql-client postgresql-client smtp-user-enum john \
        metasploit-framework ca-certificates curl \
        gobuster aircrack-ng hashcat \
        snmp snmp-mibs-downloader \
    && rm -rf /var/lib/apt/lists/* \
    # Enable SNMP MIB name resolution so symbolic OIDs (sysContact, sysDescr, ...) resolve
    # instead of erroring. Debian/Kali ship net-snmp with MIBs disabled via `mibs :` in
    # /etc/snmp/snmp.conf; download the standard MIBs and append `mibs +ALL` to re-enable.
    # Non-fatal: a transient MIB-source hiccup must not brick the expensive Kali build
    # (numeric OIDs still work either way).
    && (download-mibs || echo "WARN: download-mibs failed; use numeric SNMP OIDs") \
    && printf '\n# Load all downloaded MIBs so symbolic OIDs resolve (sysContact, sysDescr).\nmibs +ALL\n' \
        >> /etc/snmp/snmp.conf \
    # Sliver client, matching the C2 server version, for the modern C2 module.
    && curl -fL -o /usr/local/bin/sliver \
        "https://github.com/BishopFox/sliver/releases/download/${SLIVER_VERSION}/sliver-client_linux" \
    && chmod +x /usr/local/bin/sliver

# Curated lab wordlist for the SSH password-attack module. Small and deterministic so
# the brute force finishes in under a minute; the full rockyou list also works and ships
# at /usr/share/wordlists/rockyou.txt.gz (gunzip it first).
COPY wordlists/lab-passwords.txt /usr/share/wordlists/lab-passwords.txt
# Username list for the password-spraying module.
COPY wordlists/lab-users.txt /usr/share/wordlists/lab-users.txt
# Pre-captured WPA2 handshake for the offline wireless-cracking module (RF capture cannot
# be containerized; this is a real 4-way handshake for a known SSID with a crackable PSK).
COPY captures/ /root/captures/

EXPOSE 7681
# -W makes the terminal writable (interactive).
CMD ["ttyd", "-p", "7681", "-W", "bash"]
