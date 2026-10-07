#!/bin/bash
# Bring up a headless desktop and serve it over VNC with the weak password "password".
# The per-deploy flag (from the shared svc_flags volume) is placed on the desktop so a
# student who connects can read it.
set -e

FLAG="$(cat /svc/vnc_flag.txt 2>/dev/null || echo 'PENTESTTV{flag-not-planted}')"
printf 'Pentest.TV VNC host (vnc-01)\n\nRemote desktop flag:\n%s\n' "$FLAG" > /root/flag.txt

export DISPLAY=:0
rm -f /tmp/.X0-lock 2>/dev/null || true
Xvfb :0 -screen 0 1024x768x16 &
sleep 2

# Minimal window manager plus a terminal showing the flag file.
fluxbox >/dev/null 2>&1 &
sleep 1
xterm -geometry 100x30+40+40 -e "bash -lc 'cat /root/flag.txt; echo; echo \"(this terminal is the flag drop; also saved at /root/flag.txt)\"; exec bash'" &

# Set the weak VNC password and serve the display. -forever keeps it up across clients.
mkdir -p /root/.vnc
x11vnc -storepasswd password /root/.vnc/passwd
exec x11vnc -display :0 -rfbauth /root/.vnc/passwd -rfbport 5900 -forever -shared -noxdamage
