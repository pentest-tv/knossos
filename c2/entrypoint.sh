#!/bin/bash
# Initialise the Sliver server, generate an operator config for the Kali client (written
# to the shared c2_config volume), then run the team server in the foreground.
set -e
export HOME=/root

# First run unpacks bundled assets into ~/.sliver (offline, no download needed).
# Generate the operator profile the Kali client imports. --lhost is the address the
# client dials, which is this server's DMZ IP.
# Always (re)generate the operator profile so it matches this server's current CA, even
# if the container was recreated. ~/.sliver is persisted on the c2_state volume, so the CA
# is stable across restarts and the saved config stays valid for the Kali client to import.
# --save refuses to overwrite, so clear any prior config before regenerating.
rm -f /shared/operator.cfg
sliver-server operator --name operator --lhost 172.28.10.50 --lport 31337 \
  --save /shared/operator.cfg || echo "operator config generation returned non-zero (continuing)"
chmod 644 /shared/operator.cfg 2>/dev/null || true

# Run the multiplayer team server so the Kali client can connect on 31337.
exec sliver-server daemon --lhost 0.0.0.0 --lport 31337
