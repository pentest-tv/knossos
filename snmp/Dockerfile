# Network device simulation for the SNMP module. Intentionally exposes the default
# public (read) and private (read/write) community strings the book's chapter 13
# demonstrates against. Base image is pinned by digest via the BASE_DEBIAN build arg.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends snmpd \
    && rm -rf /var/lib/apt/lists/*

COPY snmpd.conf /etc/snmp/snmpd.conf
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# The entrypoint injects the per-deploy vuln-scan flag into sysDescr, then runs snmpd.
# snmpd reads /etc/snmp/snmpd.conf by default; passing it again with -c reads it twice
# and double-binds udp:161, which fails, so the entrypoint relies on the default read.
EXPOSE 161/udp
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
