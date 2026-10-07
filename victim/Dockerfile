# Simulated internal user for the Targeting the Network module. Logs into the
# target's cleartext FTP on a loop so an on-path attacker (ARP MITM on the internal
# segment) has live credentials to capture.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY loop.sh /usr/local/bin/loop.sh
RUN chmod +x /usr/local/bin/loop.sh

CMD ["/usr/local/bin/loop.sh"]
