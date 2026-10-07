#!/bin/bash
# Seeds the PostgreSQL exploitation target at first init. Runs inside the official
# image's entrypoint (local server up, psql available, POSTGRES_USER set). The server
# is started with trust auth (POSTGRES_HOST_AUTH_METHOD=trust), so any remote client
# can connect with no password: that is the misconfiguration the student exploits.
set -e

FLAG="$(cat /svc/pg_flag.txt 2>/dev/null || echo 'PENTESTTV{flag-not-planted}')"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
CREATE TABLE secrets (id int PRIMARY KEY, name text, value text);
INSERT INTO secrets VALUES (1, 'exfil_flag', '${FLAG}');
CREATE TABLE customers (id int, name text, city text);
INSERT INTO customers VALUES
  (1001,'Fictional Freight Co','Denver'),
  (1002,'Example Logistics LLC','Phoenix'),
  (1003,'Sample Shippers Inc','Dallas');
SQL

echo "postgres seed: secrets planted"
