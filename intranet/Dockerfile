# Small intranet web server for the web content-discovery module (book ch 6/14). A plain
# landing page links nothing sensitive, but a hidden /backup/ directory (hinted at in
# robots.txt and found by directory brute forcing) holds the flag. The flag file is
# planted per deploy into /srv/www/backup via the loot_web volume.
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

RUN mkdir -p /srv/www/backup
COPY www/ /srv/www/

EXPOSE 80
CMD ["python3", "-m", "http.server", "80", "--directory", "/srv/www"]
