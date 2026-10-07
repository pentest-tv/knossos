# Knossos by Pentest.TV (Docker)

Version 0.6.0

Knossos is the hands-on hacking lab and companion to Thomas Wilhelm's
*Professional Penetration Testing* (3rd Edition): the containerizable majority of the
course in a single, pinned, self-planting deploy. One command brings up the Knossos
network, waits until every target is healthy, and plants per-deploy flags automatically.
No student setup beyond Docker. Tagline: navigate the labyrinth.

> Intentionally vulnerable systems. Read SECURITY.md before running. Localhost and an
> isolated Docker network only; never expose these ports or run on a production machine.

## System requirements

Measured on a full running deploy (all 28 target containers plus the in-lab Kali,
idle): about 2.5 GB of RAM total. The heaviest services are LDAP, MySQL, and DNS;
most targets use only a few MB each. Budget headroom above that for Kali running
tools and the web apps under traffic.

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 cores | 4 cores |
| RAM (free for Docker) | 6 GB | 8 GB or more |
| Disk (images + volumes) | 25 GB | 30 to 40 GB |
| Docker | Engine with Compose v2 | Docker Desktop (WSL2 on Windows) |

- **Host OS:** Windows 10 or 11 with Docker Desktop on the WSL2 backend, macOS with
  Docker Desktop, or Linux with Docker Engine and the Compose v2 plugin.
- **Internet:** needed only for the first build and image pulls. Once built, the lab
  runs fully offline by design.
- **The heavy piece is the optional Kali box.** Its first build pulls metasploit and is
  the largest and slowest step. Bring your own Kali and skip the in-lab attacker to cut
  RAM, disk, and build time; the target range itself is light and runs comfortably on a
  16 GB laptop (or 8 GB when attacking from your own box).

## Student experience (after the repo is pinned)

```
git clone <repo> && cd lab
docker compose up -d --build                 # all targets + Kali, flags planted automatically
docker compose down -v                       # reset everything
```

The attacker box (Kali in the browser at http://localhost:7681) comes up with the rest.
The internal segment and the target's service ports are reachable only from Kali or by
pivoting through the exploited DMZ host, not from your desktop; only the DMZ web apps
publish host ports.

That is the entire interaction. Flags are planted by a one-shot service once targets
report healthy, so there is no separate script for the student to run.

## Control center

Open http://localhost:8890 for the lab's landing page and control center:

- **Onboarding:** the engagement brief and how to start.
- **Live range status:** a status dot per container (up, warning, down), auto-refreshing,
  grouped by DMZ and internal, with per-service restart and quick links to each target.
- **Reset controls:** reset your progress, re-plant flags with new values, or reset the
  entire range (restart all targets, re-plant, clear progress) in one click.
- **Scoring:** flag submission for the flag-graded modules, manual done for the rest, with
  a running score and completion bar.

Live status and controls work by talking to the Docker socket, which the panel mounts.
That is powerful (the panel can restart containers), so it is bound to localhost only.
If the socket is not available the page still runs, just without live status and controls.

## Maintainer setup (once, by you)

Images are pinned by digest, not tag, so the lab never drifts. Digests must be resolved
on a host that can reach Docker Hub:

```
cp .env.example .env
./scripts/pin-digests.sh        # Linux/macOS Docker host
# or: powershell -ExecutionPolicy Bypass -File scripts\pin-digests.ps1   (Windows)
```

This pulls each image, reads its repo digest, and writes `name@sha256:...` into `.env`.
Commit `.env`. From then on every student deploys exactly those images. `.env` holds
only public pins and ports, no secrets, so committing it is intended.

## What covers which modules

Recon (vulnerability scanning and web content discovery), Weaponization and payload
delivery (msfvenom to a victim that runs the payload), Delivery (phishing / social
engineering), Exploitation (Samba and FTP service exploits, MySQL and PostgreSQL
databases, a weak-password VNC desktop, SMTP user enumeration and open relay, a remote
SSH password attack, and password spraying), Installation/persistence, Command and
control (pivoting plus a modern Sliver C2 server), privilege escalation (local password
crack, SUID binary, and sudo misconfiguration), Actions on objectives (SMB exfiltration,
post-exploitation pillaging, credential reuse / lateral movement, and DNS data
exfiltration), Targeting the network (SNMP and ARP MITM), Wireless (offline cracking of a
provided WPA2 handshake), and Web application (DVWA plus modern Juice Shop). The
containerizable majority of the course.

Enterprise surfaces are layered on top: LDAP directory enumeration, SSO/JWT token
forgery, secrets in source control (git history and CI), credentials in an internal
wiki, central-log credential mining, offline Kerberoasting, and a deep pivot through a
jump host into a restricted segment that the attacker box cannot reach directly. Plus
enterprise "feel": an employee directory, HR and finance documents, service accounts
that span systems, a third (restricted) network tier, a central log collector, and
decoy hosts (a printer and an HR portal).

## Phishing module

Gophish is the campaign framework; MailHog catches every email so nothing leaves the
lab. Workflow: open the Gophish admin UI at http://localhost:3333 (get the generated
admin password from `docker logs pentesttv-gophish | findstr -i password`), set the
sending profile SMTP host to `mailhog:1025`, build and launch a campaign, then view the
delivered phishing emails in MailHog at http://localhost:8025. The landing server that
captures clicks and credentials is at http://localhost:8088.

## Web module tooling

GUI tools run on the student's own OS, not in the container, since the browser Kali is
terminal only. For Burp Suite: start Burp on your machine with its proxy on
127.0.0.1:8080, point your browser at it, and target the published apps (DVWA at
http://localhost:8081, Juice Shop at http://localhost:3000). DVWA sits on 8081 so it
does not collide with Burp's default 8080.

For the VNC module the viewer is also a GUI tool, so it runs on your own OS. The VNC
target is published on the host at `localhost:5901`; connect with any viewer using the
password `password`. The browser Kali ships the CLI attack tools (mysql, psql,
smtp-user-enum, hydra, john) for the database, mail, and password modules.

## What is not here, and why

Cannot containerize. Each has its own deploy path:

| Module area | Why not Docker | Where it lives |
| --- | --- | --- |
| Active Directory (C2, actions on objectives internal path) | Windows AD needs real VMs | `../range` (Ludus/Vagrant) |
| Wireless (module 11) | Needs RF or a capture file | Pre-captured handshake, cracked locally |
| Cloud (module 13) | Lives in AWS by definition | Student's own AWS account |

## Known caveat

Containers share the host kernel and have no real init, so the persistence module and
kernel-level privilege escalation behave differently than on a VM. The local privilege
escalation module here is credential-based (crack root's password from a leaked shadow
backup, then su), which works in a container; kernel-exploit privesc should be done on
the VM target. Service exploits, web, and network modules are unaffected. Run
persistence (module 8) on the VM target for fidelity.

The MySQL, PostgreSQL, VNC, and SMTP targets are purpose-built containers (not the
Metasploitable image) so their vulnerable state is deterministic. On first bring-up,
smoke-test each once: `mysql -h 172.28.10.40 -u root --skip-ssl`, `psql -h 172.28.10.41 -U postgres
-d corp`, a VNC viewer to `localhost:5901` (password `password`), and `nc 172.28.10.43 25`
then `VRFY jsmith`.

The Sliver C2 server (`c2-01`) and the Kali Sliver client download the Sliver binary at
build time from GitHub, pinned to `SLIVER_VERSION` in `.env`; the build host needs internet
(the cloud build environment does not, so this is built on your Docker host). The Kali image
also installs `metasploit-framework`, which is large, so the first Kali build is slow.
Payload delivery works through `ws-03`: a world-writable SMB share (`//172.28.20.70/drop`)
whose contents are executed as the `victim` user every ~20s, so a msfvenom payload or Sliver
implant dropped there calls back. Smoke-test the C2 chain once: `sliver import
/c2/operator.cfg` then `sliver` on Kali should connect to the server, and a test ELF dropped
in the share should run within ~20s.

The wireless module ships a pre-captured WPA2 handshake (RF capture cannot be
containerized). It lives on Kali at `/root/captures/wpa-handshake.pcap` (with a hashcat
`.22000` beside it); its crypto is generated and self-verified by `wireless/gen-handshake.py`,
so it cracks to the passphrase baked into the capture. The wireless flag is that recovered
passphrase (a Wi-Fi PSK), not a `PENTESTTV{...}` string. Smoke-test once: `aircrack-ng -w
/usr/share/wordlists/lab-passwords.txt /root/captures/wpa-handshake.pcap` should report KEY
FOUND; if aircrack rejects the pcap framing on your build, `hashcat -m 22000` on the `.22000`
file is the reliable fallback.

The enterprise surfaces use lightweight stand-ins (a self-built OpenLDAP with a static
slapd.conf, a dumb-HTTP git repo, a small Flask SSO, a static wiki, a log export). Validated:
git clone, wiki, log mining, SSO/JWT login, and the deep pivot through the jump host. The
LDAP directory is self-seeded with slapadd and allows anonymous read; smoke-test with
`ldapsearch -x -H ldap://172.28.20.90 -b dc=pentesttv,dc=local`, which should return the
employee and service entries (svc_backup's description holds a password and its info holds
the flag). The Kerberoast ticket is cryptographically valid (verified independently); crack
it with John (`john --format=krb5tgs --wordlist=/usr/share/wordlists/lab-passwords.txt
/root/captures/kerberoast.txt`), which validates on the ticket HMAC and recovers `Winter2024`.

## Topology

| Host | Network | Address | Role |
| --- | --- | --- | --- |
| pentesttv-target | dmz + internal | 172.28.10.20 / 172.28.20.20 | Linux exploitation target |
| pentesttv-web | dmz | 172.28.10.30 | DVWA web app (host port 8081) |
| pentesttv-juice | dmz | 172.28.10.31 | Juice Shop, modern web app (host port 3000) |
| pentesttv-gophish | dmz | 172.28.10.32 | Phishing framework (admin 3333, landing 8088) |
| pentesttv-mail | dmz | 172.28.10.33 | MailHog sink (UI 8025, SMTP 1025) |
| pentesttv-dns | dmz | 172.28.10.34 | Authoritative DNS, open zone transfer (recon) |
| pentesttv-mysql | dmz | 172.28.10.40 | MySQL, remote root with no password |
| pentesttv-postgres | dmz | 172.28.10.41 | PostgreSQL, trust auth (no password) |
| pentesttv-vnc | dmz | 172.28.10.42 | VNC desktop, weak password (host port 5901) |
| pentesttv-smtp | dmz | 172.28.10.43 | SMTP open relay, VRFY user enumeration |
| pentesttv-c2 | dmz + internal | 172.28.10.50 / 172.28.20.80 | Sliver C2 server (operator port 31337) |
| pentesttv-intranet | internal | 172.28.20.130 | Intranet web, hidden /backup path (host port 8082) |
| pentesttv-git | internal | 172.28.20.131 | Git/CI server, secrets in history (host port 8083) |
| pentesttv-wiki | internal | 172.28.20.132 | Internal wiki, leaks ops creds (host port 8084) |
| pentesttv-sso | dmz | 172.28.10.72 | SSO/JWT service, weak HS256 secret (host port 8085) |
| pentesttv-hrportal | dmz | 172.28.10.73 | HR portal (decoy/noise) |
| pentesttv-ldap | internal | 172.28.20.90 | LDAP directory, anonymous bind |
| pentesttv-jump | internal + restricted | 172.28.20.100 / 172.28.30.10 | Jump host into the restricted segment |
| pentesttv-syslog | internal | 172.28.20.110 | Central log collector, leaks a credential |
| pentesttv-printer | internal | 172.28.20.120 | Networked printer (decoy/noise) |
| pentesttv-vault | restricted | 172.28.30.20 | Restricted crown jewel, only via the jump host |
| pentesttv-scoreboard | dmz | dynamic | Flag submission and scoring (UI 8890) |
| pentesttv-snmp | internal | 172.28.20.40 | SNMP device simulation |
| pentesttv-pivot | internal | 172.28.20.50 | Internal foothold: SSH password attack, C2, persistence |
| pentesttv-files | internal | 172.28.20.60 | Crown-jewel SMB file server (exfil target) |
| pentesttv-victim | internal | 172.28.20.61 | Simulated user generating cleartext FTP for ARP MITM |
| pentesttv-workstation | internal | 172.28.20.70 | Payload-delivery victim, writable SMB drop share |
| pentesttv-kali | dmz + internal | 172.28.10.10 / 172.28.20.10 | Kali attacker, browser terminal at :7681 |

The internal network has no outbound route, so the student must pivot through the DMZ
to reach it, like a real engagement.

## Flags

Planted automatically by the `flag-init` service: `/root/ctf/` on the target, the pivot
loot volume, the file server share (`\\pentesttv-files\data\loot\exfil_flag.txt`), a
root-only file on the pivot for the privilege-escalation module, and the `svc_flags`
volume that the MySQL, PostgreSQL, and VNC targets read at startup to plant their own
flags. Values are random per deploy and recorded in `flags.generated.env` for the
platform validator. That file is gitignored.

Note: the database and VNC flags are seeded when those containers first initialize, so
the scoreboard "Re-plant flags" button (which re-runs `flag-init`) rotates the file-based
flags immediately; to rotate the database and VNC flags, recreate the range with
`docker compose down -v` then `up -d --build`.

## Robustness notes

- Healthchecks gate startup; `flag-init` waits for targets to be healthy before planting.
- `restart: unless-stopped` keeps targets up across host reboots.
- Images pinned by digest; rebuild is reproducible.
- Reset is one command: `docker compose down -v`.

## Troubleshooting

Fixes already baked into the committed files, recorded here for maintainers.

- **Target restart-looping.** The Metasploitable image starts its services then exits,
  so `restart: unless-stopped` looped it. Fixed by running the services script and
  holding the container open: `command: /bin/sh -c "/bin/services.sh && tail -f /dev/null"`.
- **Stack aborts on "target is unhealthy".** `flag-init` originally waited for the target
  to be healthy. It only needs the container running to drop flag files, so it now depends
  on `service_started`, not `service_healthy`.
- **snmp exits with code 1, "Error opening specified endpoint udp:161".** snmpd reads
  `/etc/snmp/snmpd.conf` by default, and passing it again with `-c` read it twice and
  double-bound 161. Fixed by dropping `-c`: `CMD ["snmpd","-f","-Lo"]`.
- **Target shows "unhealthy" though services are up.** The `bash /dev/tcp` healthcheck is
  flaky on the old image. Switched to `netstat -ltn | grep ':21 '`, which that image
  supports.
- **`ss` / `ss-lun` not found in a container.** The slim images ship `netstat`, not `ss`.
  Use `netstat -ltn` (TCP) when checking listeners.
