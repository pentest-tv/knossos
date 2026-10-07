#!/usr/bin/env python3
"""Pentest.TV lab control center: landing page, live status, reset controls, and scoring.

Single-student, local. Reads per-deploy flags from a mounted file, renders the course
and the live range from Docker, validates submitted flags, and controls containers
(restart, re-plant flags, reset) through the mounted Docker socket.
"""
import base64
import json
import os
import sqlite3
import threading
import time
from pathlib import Path

from flask import Flask, g, jsonify, redirect, render_template, request, url_for, flash

APP_DIR = Path(__file__).resolve().parent
COURSE_FILE = APP_DIR / "course.json"
FLAGS_FILE = Path(os.environ.get("FLAGS_FILE", "/app/flags/flags.env"))
DB_FILE = Path(os.environ.get("DB_FILE", "/app/db/scoreboard.sqlite"))
PROJECT = os.environ.get("COMPOSE_PROJECT", "pentesttv-lab")

# Escape-the-Labyrinth finale: the reward claim handoff to Pentest.TV. The passphrase has
# NO default and must be supplied via the KNOSSOS_CLAIM_PASS environment variable to enable
# the reward; left unset, the finale still celebrates completion but shows no claim. When set,
# the claim URL and passphrase are woven (reversed, then base64) into the finale page source
# so completers do one last extraction to claim their reward.
CLAIM_URL = os.environ.get("KNOSSOS_CLAIM_URL", "https://pentest.tv/knossos/claim")
CLAIM_PASS = os.environ.get("KNOSSOS_CLAIM_PASS", "")


def _escape_thread():
    payload = (
        "KNOSSOS OPERATOR -- you navigated the Labyrinth and reached the center. "
        f"Claim your badge, Discord role, and certificate at: {CLAIM_URL}  "
        f"| passphrase: {CLAIM_PASS}"
    )
    # reverse, then base64: the rendered page only hints; the thread lives in the source.
    return base64.b64encode(payload[::-1].encode("utf-8")).decode("ascii")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pentesttv-lab-local")

# Service catalog: how each container maps to zone, link, and modules.
SERVICES = [
    {"name": "pentesttv-target", "label": "Linux target", "zone": "DMZ", "url": None,
     "modules": "Exploitation, Installation", "ip": "172.28.10.20, 172.28.20.20", "host": "dmz-01.pentesttv.local"},
    {"name": "pentesttv-web", "label": "DVWA", "zone": "DMZ", "url": "http://localhost:8081",
     "modules": "Web application", "ip": "172.28.10.30", "host": "web-01.pentesttv.local"},
    {"name": "pentesttv-juice", "label": "Juice Shop", "zone": "DMZ", "url": "http://localhost:3000",
     "modules": "Modern web", "ip": "172.28.10.31", "host": "web-02.pentesttv.local"},
    {"name": "pentesttv-gophish", "label": "Gophish", "zone": "DMZ", "url": "http://localhost:3333",
     "modules": "Phishing", "ip": "172.28.10.32", "host": "phish-01.pentesttv.local"},
    {"name": "pentesttv-mail", "label": "MailHog", "zone": "DMZ", "url": "http://localhost:8025",
     "modules": "Phishing", "ip": "172.28.10.33", "host": "mail-01.pentesttv.local"},
    {"name": "pentesttv-dns", "label": "DNS server", "zone": "DMZ", "url": None,
     "modules": "Reconnaissance", "ip": "172.28.10.34", "host": "dns-01.pentesttv.local"},
    {"name": "pentesttv-mysql", "label": "MySQL", "zone": "DMZ", "url": None,
     "modules": "Database exploitation", "ip": "172.28.10.40", "host": "db-01.pentesttv.local"},
    {"name": "pentesttv-postgres", "label": "PostgreSQL", "zone": "DMZ", "url": None,
     "modules": "Database exploitation", "ip": "172.28.10.41", "host": "db-02.pentesttv.local"},
    {"name": "pentesttv-vnc", "label": "VNC desktop", "zone": "DMZ", "url": None,
     "modules": "Remote desktop", "ip": "172.28.10.42", "host": "vnc-01.pentesttv.local"},
    {"name": "pentesttv-smtp", "label": "SMTP relay", "zone": "DMZ", "url": None,
     "modules": "Mail enumeration", "ip": "172.28.10.43", "host": "smtp-01.pentesttv.local"},
    {"name": "pentesttv-c2", "label": "Sliver C2", "zone": "DMZ", "url": None,
     "modules": "Command and control", "ip": "172.28.10.50, 172.28.20.80", "host": "c2-01.pentesttv.local"},
    {"name": "pentesttv-intranet", "label": "Intranet web", "zone": "Internal", "url": "http://localhost:8082",
     "modules": "Web content discovery", "ip": "172.28.20.130", "host": "web-03.pentesttv.local"},
    {"name": "pentesttv-git", "label": "Git / CI server", "zone": "Internal", "url": "http://localhost:8083",
     "modules": "Secrets sprawl, CI/CD", "ip": "172.28.20.131", "host": "git-01.pentesttv.local"},
    {"name": "pentesttv-wiki", "label": "Internal wiki", "zone": "Internal", "url": "http://localhost:8084",
     "modules": "Enterprise knowledge base", "ip": "172.28.20.132", "host": "wiki-01.pentesttv.local"},
    {"name": "pentesttv-sso", "label": "SSO / JWT", "zone": "DMZ", "url": "http://localhost:8085",
     "modules": "Token attacks", "ip": "172.28.10.72", "host": "sso-01.pentesttv.local"},
    {"name": "pentesttv-hrportal", "label": "HR portal (decoy)", "zone": "DMZ", "url": None,
     "modules": "Scale / noise", "ip": "172.28.10.73", "host": "hr-app-01.pentesttv.local"},
    {"name": "pentesttv-ldap", "label": "LDAP directory", "zone": "Internal", "url": None,
     "modules": "Directory enumeration", "ip": "172.28.20.90", "host": "ldap-01.pentesttv.local"},
    {"name": "pentesttv-jump", "label": "Jump host", "zone": "Internal", "url": None,
     "modules": "Pivot to restricted", "ip": "172.28.20.100", "host": "jump-01.pentesttv.local"},
    {"name": "pentesttv-syslog", "label": "Log collector", "zone": "Internal", "url": None,
     "modules": "Log mining", "ip": "172.28.20.110", "host": "log-01.pentesttv.local"},
    {"name": "pentesttv-printer", "label": "Printer (decoy)", "zone": "Internal", "url": None,
     "modules": "Scale / noise", "ip": "172.28.20.120", "host": "print-01.pentesttv.local"},
    {"name": "pentesttv-vault", "label": "Restricted vault", "zone": "Restricted", "url": None,
     "modules": "Crown jewel (restricted)", "ip": "172.28.30.20", "host": "vault-01.pentesttv.local"},
    {"name": "pentesttv-workstation", "label": "Workstation", "zone": "Internal", "url": None,
     "modules": "Payload delivery, post-ex", "ip": "172.28.20.70", "host": "ws-03.pentesttv.local"},
    {"name": "pentesttv-snmp", "label": "SNMP device", "zone": "Internal", "url": None,
     "modules": "Targeting the network", "ip": "172.28.20.40", "host": "net-01.pentesttv.local"},
    {"name": "pentesttv-pivot", "label": "Pivot host", "zone": "Internal", "url": None,
     "modules": "C2, Persistence", "ip": "172.28.20.50", "host": "ws-01.pentesttv.local"},
    {"name": "pentesttv-files", "label": "File server", "zone": "Internal", "url": None,
     "modules": "Actions on objectives", "ip": "172.28.20.60", "host": "files-01.pentesttv.local"},
    {"name": "pentesttv-victim", "label": "Victim user", "zone": "Internal", "url": None,
     "modules": "Network (MITM)", "ip": "172.28.20.61", "host": "ws-02.pentesttv.local"},
    {"name": "pentesttv-kali", "label": "Kali attacker", "zone": "Attack Platform", "url": "http://localhost:7681",
     "modules": "Attacker box", "buildable": True, "ip": "172.28.10.10, 172.28.20.10", "host": "attacker.pentesttv.local"},
]
CONTROL = {"pentesttv-scoreboard", "pentesttv-flaginit"}

# Background state for the optional-attacker install.
_install = {"running": False, "error": None}


# ---- Docker -------------------------------------------------------------------
_CLIENT = None

def docker_client():
    # Cache the client: docker.from_env() renegotiates the API version over the
    # socket on every call, which is the bulk of the panel's refresh latency.
    global _CLIENT
    if _CLIENT is None:
        try:
            import docker
            _CLIENT = docker.from_env()
        except Exception:
            _CLIENT = None
    return _CLIENT


def container_states():
    """Return {name: {'state':..., 'health':...}} for project containers, or {}.

    Uses the low-level /containers/json endpoint (one request) instead of
    containers.list(), which does a full inspect per container -- that per-item
    inspect storm made the panel take ~9s once the whole lab was running.
    """
    client = docker_client()
    if client is None:
        return {}
    out = {}
    try:
        rows = client.api.containers(
            all=True, filters={"label": f"com.docker.compose.project={PROJECT}"})
        for r in rows:
            name = (r.get("Names") or ["/?"])[0].lstrip("/")
            state = r.get("State", "")           # running / exited / created / restarting ...
            status = r.get("Status", "")          # e.g. "Up 3 minutes (healthy)"
            if "(healthy)" in status:
                health = "healthy"
            elif "(unhealthy)" in status:
                health = "unhealthy"
            elif "health: starting" in status:
                health = "starting"
            else:
                health = None
            nets = (r.get("NetworkSettings") or {}).get("Networks") or {}
            ips = sorted(v.get("IPAddress") for v in nets.values() if v.get("IPAddress"))
            out[name] = {"state": state, "health": health, "ips": ips, "host": ""}
    except Exception:
        # Drop the cached client so the next call rebuilds it (self-heal).
        global _CLIENT
        _CLIENT = None
        return {}
    return out


_STATUS_TTL = 2.0
_status_cache = {"t": 0.0, "val": None}

def service_status(force=False):
    # Serve a cached result for up to _STATUS_TTL seconds so the page load and the
    # 5s poll do not each hammer the Docker socket.
    now = time.monotonic()
    cached = _status_cache["val"]
    if not force and cached is not None and (now - _status_cache["t"]) < _STATUS_TTL:
        return cached
    states = container_states()
    rows = []
    for svc in SERVICES:
        st = states.get(svc["name"], {})
        state = st.get("state", "absent")
        health = st.get("health")
        if health == "healthy" or (state == "running" and not health):
            level = "up"
        elif state in ("restarting", "created") or health == "starting":
            level = "warn"
        elif state == "running" and health == "unhealthy":
            level = "warn"
        else:
            level = "down"
        installing = _install["running"] and bool(svc.get("buildable"))
        if installing:
            level = "warn"
        live_ips = st.get("ips") or []
        rows.append({**svc, "state": state, "health": health or "-", "level": level,
                     "ip": ", ".join(live_ips) if live_ips else svc.get("ip", ""),
                     "host": st.get("host") or svc.get("host", ""),
                     "installing": installing,
                     "installable": bool(svc.get("buildable") and state == "absent" and not installing)})
    result = (rows, docker_client() is not None)
    _status_cache["t"] = now
    _status_cache["val"] = result
    return result


# ---- DB -----------------------------------------------------------------------
def db():
    if "db" not in g:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
        g.db.execute(
            "CREATE TABLE IF NOT EXISTS progress ("
            "module_id TEXT PRIMARY KEY, status TEXT NOT NULL, solved_at TEXT)"
        )
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def solved_set():
    return {r["module_id"] for r in db().execute("SELECT module_id FROM progress WHERE status='solved'")}


def load_course():
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def load_flags():
    flags = {}
    try:
        for line in FLAGS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                flags[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return flags


# ---- Views --------------------------------------------------------------------
@app.route("/")
def index():
    course = load_course()
    done = solved_set()
    modules = course["modules"]
    for m in modules:
        m["solved"] = m["id"] in done
    total = len(modules)
    solved = sum(1 for m in modules if m["solved"])
    pct = round(solved / total * 100) if total else 0
    # Group modules into their kill-chain phases (preserving first-seen order)
    # so the panel can render one collapsible bubble per phase.
    phases = []
    _by_phase = {}
    for m in modules:
        ph = m.get("phase") or "Modules"
        g = _by_phase.get(ph)
        if g is None:
            g = {"name": ph, "n": len(phases) + 1, "modules": [], "solved": 0, "total": 0}
            _by_phase[ph] = g
            phases.append(g)
        g["modules"].append(m)
        g["total"] += 1
        if m["solved"]:
            g["solved"] += 1
    if _install.get("error"):
        flash(("error", f"Kali install failed: {_install['error']}"))
        _install["error"] = None
    status, docker_ok = service_status()
    zones = {"Attack Platform": [s for s in status if s["zone"] == "Attack Platform"],
             "DMZ": [s for s in status if s["zone"] == "DMZ"],
             "Internal": [s for s in status if s["zone"] == "Internal"],
             "Restricted": [s for s in status if s["zone"] == "Restricted"]}
    return render_template(
        "index.html", course=course["course"], book=course.get("book"),
        book2=course.get("book2"),
        scope=course.get("scope"),
        modules=modules, phases=phases, solved=solved, total=total, pct=pct,
        complete=(solved == total and total > 0), zones=zones, docker_ok=docker_ok,
    )


@app.route("/escape")
def escape():
    """The 100% finale. Only weaves in the hidden claim thread once every flag is captured;
    otherwise it shows a locked state so the reward cannot be reached early."""
    course = load_course()
    done = solved_set()
    total = len(course["modules"])
    solved = sum(1 for m in course["modules"] if m["id"] in done)
    complete = solved == total and total > 0
    reward = complete and bool(CLAIM_PASS)
    return render_template(
        "escape.html", complete=complete, solved=solved, total=total,
        reward_configured=bool(CLAIM_PASS),
        thread=(_escape_thread() if reward else ""),
    )


@app.route("/status")
def status_json():
    rows, docker_ok = service_status()
    return jsonify({"docker_ok": docker_ok,
                    "services": {r["name"]: {"level": r["level"], "state": r["state"],
                                             "health": r["health"]} for r in rows}})


@app.route("/submit", methods=["POST"])
def submit():
    module_id = request.form.get("module_id", "")
    submitted = request.form.get("flag", "").strip()
    module = next((m for m in load_course()["modules"] if m["id"] == module_id), None)
    if not module or module.get("grading") != "flag":
        flash(("error", "Unknown flag module."))
        return redirect(url_for("index") + "#status")
    expected = load_flags().get(module.get("flag_var", ""))
    if not expected:
        flash(("error", f"No flag loaded for {module['title']}. Is the lab deployed?"))
    elif submitted == expected:
        db().execute("INSERT OR REPLACE INTO progress VALUES (?, 'solved', datetime('now'))", (module_id,))
        db().commit()
        flash(("success", f"Correct. {module['title']} solved."))
    else:
        flash(("error", "Incorrect flag. Check the PENTESTTV{...} format and try again."))
    return redirect(url_for("index") + "#status")


@app.route("/complete", methods=["POST"])
def complete():
    module_id = request.form.get("module_id", "")
    module = next((m for m in load_course()["modules"] if m["id"] == module_id), None)
    if not module or module.get("grading") != "manual":
        flash(("error", "Unknown module."))
        return redirect(url_for("index") + "#status")
    if module_id in solved_set():
        db().execute("DELETE FROM progress WHERE module_id=?", (module_id,))
        flash(("success", f"{module['title']} marked not done."))
    else:
        db().execute("INSERT OR REPLACE INTO progress VALUES (?, 'solved', datetime('now'))", (module_id,))
        flash(("success", f"{module['title']} marked done."))
    db().commit()
    return redirect(url_for("index") + "#status")


# ---- Controls -----------------------------------------------------------------
def _get(client, name):
    try:
        return client.containers.get(name)
    except Exception:
        return None


def _rerun_flaginit_and_reload(client):
    """Regenerate flags (and the DNS zone), then reload the DNS server so the new
    zone-transfer flag is served. flag-init MUST fully finish rewriting the zone and
    flags.env before dns restarts, or dns reloads the old zone and the AXFR flag no
    longer matches the scoreboard's expected value."""
    fi = _get(client, "pentesttv-flaginit")
    if fi:
        fi.start()
        # Let the restart take effect so we wait on the NEW run, not the prior exit,
        # then block until flag-init exits (zone + flags.env both written).
        time.sleep(1.0)
        try:
            fi.wait(timeout=120)
        except Exception:
            # Fall back to polling for the exited state if wait() is unavailable.
            for _ in range(60):
                try:
                    fi.reload()
                    if fi.status == "exited":
                        break
                except Exception:
                    break
                time.sleep(0.5)
    dns = _get(client, "pentesttv-dns")
    if dns:
        try:
            dns.restart()
        except Exception:
            pass
    # Targets that bake their flag from the svc_flags volume at startup re-read it on
    # restart, so a re-plant rotates their flag too.
    for n in ("pentesttv-snmp", "pentesttv-smtp", "pentesttv-vnc"):
        t = _get(client, n)
        if t:
            try:
                t.restart()
            except Exception:
                pass
    # MySQL/PostgreSQL seed their flag only on first init (the data dir persists), so a
    # restart cannot rotate them. Re-apply the freshly planted flag in place, reading the
    # current value from the shared svc_flags volume inside each container.
    mdb = _get(client, "pentesttv-mysql")
    if mdb:
        try:
            mdb.exec_run(["bash", "-lc",
                "mysql -uroot -e \"UPDATE corp.secrets SET value='$(cat /svc/mysql_flag.txt)' "
                "WHERE name='exfil_flag';\""])
        except Exception:
            pass
    pdb = _get(client, "pentesttv-postgres")
    if pdb:
        try:
            pdb.exec_run(["bash", "-lc",
                "psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -c "
                "\"UPDATE secrets SET value='$(cat /svc/pg_flag.txt)' WHERE name='exfil_flag';\""])
        except Exception:
            pass


@app.route("/control/restart", methods=["POST"])
def restart_one():
    name = request.form.get("name", "")
    client = docker_client()
    if client is None:
        flash(("error", "Docker control unavailable (socket not mounted)."))
        return redirect(url_for("index") + "#labstatus")
    c = _get(client, name)
    if c and name not in CONTROL:
        c.restart()
        _status_cache["val"] = None
        flash(("success", f"Restarted {name}."))
    else:
        flash(("error", f"Cannot restart {name}."))
    return redirect(url_for("index") + "#labstatus")


@app.route("/control/replant", methods=["POST"])
def replant():
    client = docker_client()
    if client is None:
        flash(("error", "Docker control unavailable (socket not mounted)."))
        return redirect(url_for("index") + "#status")
    if _get(client, "pentesttv-flaginit"):
        _rerun_flaginit_and_reload(client)
        db().execute("DELETE FROM progress")
        db().commit()
        _status_cache["val"] = None
        flash(("success", "Flags re-planted with new values. Progress reset."))
    else:
        flash(("error", "flag-init container not found."))
    return redirect(url_for("index") + "#status")


@app.route("/control/reset-range", methods=["POST"])
def reset_range():
    client = docker_client()
    if client is None:
        flash(("error", "Docker control unavailable (socket not mounted)."))
        return redirect(url_for("index") + "#status")
    skip = CONTROL | {"pentesttv-dns"}  # dns is restarted after flag-init rewrites its zone
    restarted = 0
    for c in client.containers.list(all=True, filters={"label": f"com.docker.compose.project={PROJECT}"}):
        if c.name not in skip:
            try:
                c.restart()
                restarted += 1
            except Exception:
                pass
    _rerun_flaginit_and_reload(client)
    db().execute("DELETE FROM progress")
    db().commit()
    _status_cache["val"] = None
    flash(("success", f"Lab reset: {restarted} targets restarted, flags re-planted, progress cleared."))
    return redirect(url_for("index") + "#status")


def _find_net(client, which):
    nets = client.networks.list(filters={"label": [
        f"com.docker.compose.project={PROJECT}", f"com.docker.compose.network={which}"]})
    return nets[0] if nets else None


def _do_install():
    """Build and run the optional Kali attacker, matching the compose definition."""
    try:
        client = docker_client()
        base = os.environ.get("BASE_KALI", "kalilinux/kali-rolling:latest")
        client.images.build(path="/project/attacker", tag=f"{PROJECT}-attacker",
                            buildargs={"BASE_KALI": base}, rm=True)
        dmz, internal = _find_net(client, "dmz"), _find_net(client, "internal")
        kwargs = dict(image=f"{PROJECT}-attacker", name="pentesttv-kali", hostname="attacker",
                      detach=True, ports={"7681/tcp": 7681}, cap_add=["NET_ADMIN", "NET_RAW"],
                      restart_policy={"Name": "unless-stopped"},
                      labels={"com.docker.compose.project": PROJECT,
                              "com.docker.compose.service": "attacker"})
        if dmz:
            kwargs["network"] = dmz.name
        c = client.containers.run(**kwargs)
        if internal:
            internal.connect(c)
    except Exception as e:  # surfaced to the user on next page load
        _install["error"] = str(e)
    finally:
        _install["running"] = False


@app.route("/control/install", methods=["POST"])
def install_attacker():
    client = docker_client()
    if client is None:
        flash(("error", "Docker control unavailable (socket not mounted)."))
    elif _install["running"]:
        flash(("success", "Kali install already running. Watch the status dot."))
    elif _get(client, "pentesttv-kali"):
        flash(("success", "Kali is already installed."))
    else:
        _install.update(running=True, error=None)
        _status_cache["val"] = None
        threading.Thread(target=_do_install, daemon=True).start()
        flash(("success", "Installing Kali in the background. The first build pulls the image "
                          "and takes a few minutes; the dot turns green when it is ready."))
    return redirect(url_for("index") + "#labstatus")


@app.route("/control/reset-progress", methods=["POST"])
def reset_progress():
    db().execute("DELETE FROM progress")
    db().commit()
    flash(("success", "Your progress was reset. Flags unchanged."))
    return redirect(url_for("index") + "#status")


if __name__ == "__main__":
    # threaded=True so the page, static assets, and the background /status poll
    # do not serialize through one worker (the cause of multi-second reload stalls).
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8888")), threaded=True)
