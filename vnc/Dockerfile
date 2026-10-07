# Weak-password VNC desktop for the Remote Desktop exploitation module (book ch 9, VNC).
# A headless X server (Xvfb) plus x11vnc serving an xterm session, protected only by the
# classic weak password "password". Connecting with it drops the student onto a desktop
# where the per-deploy flag is waiting. Base image pinned by digest via BASE_DEBIAN.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        xvfb x11vnc xterm fluxbox \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5900
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
