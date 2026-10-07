# Internal source/CI server (git-01), a lightweight stand-in for GitLab/Gitea. It serves
# a repository over dumb HTTP whose git history still contains a secret that was "removed"
# in a later commit, plus a CI pipeline file with hardcoded deploy credentials. Teaches
# secrets sprawl and CI/supply-chain credential theft without a heavy platform.
ARG BASE_DEBIAN=debian:stable-slim
FROM ${BASE_DEBIAN}

RUN apt-get update \
    && apt-get install -y --no-install-recommends git python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY build-repo.sh /tmp/build-repo.sh
RUN chmod +x /tmp/build-repo.sh && /tmp/build-repo.sh && rm -f /tmp/build-repo.sh

EXPOSE 80
CMD ["python3", "-m", "http.server", "80", "--directory", "/srv/git"]
