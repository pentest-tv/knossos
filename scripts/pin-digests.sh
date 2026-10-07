#!/usr/bin/env bash
# Run ONCE on a Docker host that can reach Docker Hub. Pulls each image, reads its
# repo digest, and writes the pinned refs into .env. Commit the resulting .env so
# students deploy exactly these images. Re-run to update pins deliberately.
set -euo pipefail

declare -A TAGS=(
  [TARGET_IMAGE]="tleemcjr/metasploitable2:latest"
  [DVWA_IMAGE]="vulnerables/web-dvwa:latest"
  [JUICE_IMAGE]="bkimminich/juice-shop:latest"
  [GOPHISH_IMAGE]="gophish/gophish:latest"
  [MAILHOG_IMAGE]="mailhog/mailhog:latest"
  [BIND_IMAGE]="internetsystemsconsortium/bind9:9.20"
  [PYTHON_IMAGE]="python:3.12-slim"
  [BASE_DEBIAN]="debian:stable-slim"
  [BASE_KALI]="kalilinux/kali-rolling:latest"
)

ENV_FILE=".env"
[ -f "$ENV_FILE" ] || cp .env.example "$ENV_FILE"

for var in "${!TAGS[@]}"; do
  tag="${TAGS[$var]}"
  echo "pulling $tag ..."
  docker pull "$tag" >/dev/null
  pinned="$(docker inspect --format '{{index .RepoDigests 0}}' "$tag")"
  if [ -z "$pinned" ]; then
    echo "ERROR: no repo digest for $tag" >&2
    exit 1
  fi
  echo "  $var=$pinned"
  # Replace or append the line in .env.
  if grep -q "^${var}=" "$ENV_FILE"; then
    sed -i.bak "s#^${var}=.*#${var}=${pinned}#" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "${var}=${pinned}" >> "$ENV_FILE"
  fi
done

echo "Done. Pinned digests written to $ENV_FILE. Commit it."
