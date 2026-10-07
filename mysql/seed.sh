#!/bin/bash
# Seeds the MySQL exploitation target at first init. Runs inside the official image's
# entrypoint (local server already up, mysql client available). Reads the per-deploy
# flag from the shared svc_flags volume and plants it in a table, then opens a weak,
# remotely reachable root account (the misconfiguration the student exploits).
set -e

FLAG="$(cat /svc/mysql_flag.txt 2>/dev/null || echo 'PENTESTTV{flag-not-planted}')"

mysql -uroot <<SQL
CREATE DATABASE IF NOT EXISTS corp;
USE corp;
CREATE TABLE IF NOT EXISTS secrets (id INT PRIMARY KEY, name VARCHAR(64), value VARCHAR(160));
INSERT INTO secrets VALUES (1, 'exfil_flag', '${FLAG}')
  ON DUPLICATE KEY UPDATE value = VALUES(value);
CREATE TABLE IF NOT EXISTS customers (id INT, name VARCHAR(64), city VARCHAR(64));
INSERT INTO customers VALUES
  (1001,'Fictional Freight Co','Denver'),
  (1002,'Example Logistics LLC','Phoenix'),
  (1003,'Sample Shippers Inc','Dallas');

-- Deliberately weak: root reachable from anywhere with no password. native_password
-- keeps the empty-password login working over a plain (non-TLS) client connection.
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL

echo "mysql seed: corp.secrets planted, remote root enabled"
