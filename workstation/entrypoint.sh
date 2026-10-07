#!/bin/bash
# Start the SMB server (for the writable drop share) in the background, then run the
# execution loop in the foreground as PID 1.
set -e
smbd --foreground --no-process-group --debuglevel=0 &
exec /usr/local/bin/runner.sh
