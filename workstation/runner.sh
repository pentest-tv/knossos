#!/bin/bash
# Execute any new file dropped into the SMB share as the low-privilege "victim" user,
# then move it aside. This stands in for a user double-clicking an emailed attachment, so
# a reverse-shell payload or C2 implant placed in the share calls back to the student.
set -u
DROP=/srv/drop
DONE=/srv/drop/done
mkdir -p "$DONE"

while true; do
  shopt -s nullglob
  for f in "$DROP"/*; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    run="/tmp/$base"
    cp "$f" "$run" 2>/dev/null || continue
    chmod +x "$run" 2>/dev/null || true
    # Run detached as the victim user; ignore failures so one bad drop does not stop the loop.
    su victim -c "'$run'" >/dev/null 2>&1 &
    mv -f "$f" "$DONE/$base" 2>/dev/null || rm -f "$f"
  done
  sleep 20
done
