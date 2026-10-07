# Security and safe-use notice

This repository deploys intentionally vulnerable systems for authorized security
training. Treat it accordingly.

## Rules for running this lab

- Run it only on a machine you control, for your own learning or teaching.
- Keep it isolated. The Compose file binds only to localhost and puts targets on a
  private Docker network with no inbound route from your LAN. Do not forward or expose
  these ports to other hosts or the internet.
- Never deploy on a production, shared, or internet-facing machine.
- Tear it down when done: `docker compose down -v`.

## The control center and the Docker socket

The scoreboard control center mounts the host Docker socket so it can show live status and
restart or reset containers. Anyone who can reach that web page can control Docker on the
host, so it is published to localhost only. Do not expose port 8890 beyond the local
machine, and do not run the lab where untrusted users can reach that port.

## What is intentionally weak

The targets ship with known-vulnerable services, default SNMP community strings, and a
weak account credential. That is the point of the lab. None of it is a defect to report.

## What this lab teaches

Techniques are for use only against systems you own or are explicitly authorized to
test. Applying them to systems without permission is illegal in most jurisdictions and
violates the professional ethics this course teaches (see Module 0).

## Reporting a real issue

If you find a problem in the lab tooling itself (the Compose setup, scripts, or
pipeline), not in the intentionally vulnerable targets, open an issue.
