# Runbook

Exact commands for the Pentest.TV lab on a Windows Docker host (PowerShell). Run from
the `lab` folder. Verified 2026-10-04.

## First-time setup (maintainer, once)

```powershell
cd "$HOME\OneDrive\Documents\course\lab"
powershell -ExecutionPolicy Bypass -File scripts\pin-digests.ps1   # pin image digests into .env, then commit .env
```

## Start the lab

```powershell
docker compose up -d --build
```

This brings up every target plus the Kali attacker. The first run builds and pulls Kali,
so it takes a few minutes. Wait about 45 seconds for the target healthcheck grace period,
then:

```powershell
docker compose ps
```

Expected: `pivot` healthy, `web` healthy, `snmp` up (161/udp), `target-linux` healthy,
`flaginit` exited (0).

## Verify flags were planted

```powershell
type flags.generated.env
docker exec pentesttv-target cat /root/ctf/lab_flag.txt
```

The second value should match `MODULE_07_LAB_FLAG` in the first.

## Attacker box

Kali comes up with the lab. Open http://localhost:7681 for the browser terminal. The
internal hosts and the target's service ports are reachable only from here or by pivoting
through the exploited DMZ host. The web targets are http://localhost:8081 (DVWA) and
http://localhost:3000 (Juice Shop).

## Reset (fresh flags next start)

```powershell
docker compose down -v
```

## Rebuild one service after a change

```powershell
docker compose up -d --build <service>   # e.g. snmp, pivot, attacker
```

## Recreate one service after a compose change (no rebuild)

```powershell
docker compose up -d <service>           # e.g. target-linux
```
