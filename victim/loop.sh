#!/bin/sh
# Generates cleartext FTP logins to the target over the internal segment so a
# student performing an ARP MITM can capture the credentials. Lab traffic only.
while true; do
  curl -s --max-time 10 "ftp://msfadmin:msfadmin@target-linux/" >/dev/null 2>&1 || true
  sleep 25
done
