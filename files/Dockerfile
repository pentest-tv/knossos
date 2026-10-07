# Crown-jewel internal file server for the Actions on Objectives module. Serves a
# guest-readable SMB share with planted "sensitive" data the student exfiltrates.
# The exfil flag is written at deploy into /srv/share/loot via a shared volume.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends samba \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /srv/share/loot

COPY smb.conf /etc/samba/smb.conf
COPY data/ /srv/share/

EXPOSE 139 445
CMD ["smbd", "--foreground", "--no-process-group", "--debuglevel=1"]
