# Self-built OpenLDAP directory (ldap-01). A static slapd.conf plus an LDIF seeded at
# build time with slapadd, so the directory is deterministic (unlike image-driven seeding).
# Anonymous bind can read the whole tree, including a service account whose password sits
# in a description field and the module flag in an info field.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends slapd ldap-utils \
    && rm -rf /var/lib/apt/lists/* \
    # Drop the package's auto-generated config/db; we use a static slapd.conf instead.
    && rm -rf /etc/ldap/slapd.d/* /var/lib/ldap/* \
    && mkdir -p /var/lib/ldap /var/run/slapd

COPY slapd.conf /etc/ldap/slapd.conf
COPY bootstrap.ldif /tmp/bootstrap.ldif

# Seed the database offline at build time, then hand ownership to the slapd user.
RUN slapadd -f /etc/ldap/slapd.conf -l /tmp/bootstrap.ldif \
    && chown -R openldap:openldap /var/lib/ldap /var/run/slapd \
    && rm -f /tmp/bootstrap.ldif

EXPOSE 389
CMD ["slapd", "-f", "/etc/ldap/slapd.conf", "-h", "ldap://0.0.0.0:389/", "-d", "256", "-u", "openldap", "-g", "openldap"]
