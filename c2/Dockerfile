# Dedicated Sliver C2 server (book ch 11, modern command and control). Runs the Sliver
# team server as a daemon; the student drives it from a Sliver client on the Kali box.
# Implants generated here beacon back to this server, emulating real-world C2 infra that
# is separate from the operator's workstation.
#
# The Sliver binary is downloaded at build time (your Docker host needs internet, which
# it has; the cloud build environment does not). The version is pinned via SLIVER_VERSION.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

ARG SLIVER_VERSION=v1.5.43
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fL -o /usr/local/bin/sliver-server \
        "https://github.com/BishopFox/sliver/releases/download/${SLIVER_VERSION}/sliver-server_linux" \
    && chmod +x /usr/local/bin/sliver-server

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 31337 operator (multiplayer) gRPC; 8888 default mTLS implant listener the student starts.
EXPOSE 31337 8888
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
