# Internal knowledge base / wiki (wiki-01), a lightweight stand-in for Confluence. Its
# pages are readable and, as in many real enterprises, leak credentials in prose: an IT
# runbook exposes the jump-host operations account, which is the way into the restricted
# segment. One page also carries the module flag.
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

COPY www/ /srv/www/

EXPOSE 80
CMD ["python3", "-m", "http.server", "80", "--directory", "/srv/www"]
