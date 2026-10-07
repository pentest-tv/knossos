#!/bin/bash
# Build the webapp repo with a secret committed then "removed", plus a CI pipeline with
# hardcoded creds, and publish it as a dumb-HTTP bare repo under /srv/git.
set -e
git config --global user.email "dev@pentesttv.local"
git config --global user.name "Dev Pipeline"
git config --global init.defaultBranch main

mkdir -p /build/webapp && cd /build/webapp
git init -q

cat > app.py <<'EOF'
# Pentest.TV internal web application
from config import DB_USER, DB_PASS, API_KEY
DB_HOST = "db-01.pentesttv.local"
EOF

# Commit 1: config with hardcoded secrets (the mistake).
cat > config.py <<'EOF'
# TODO: move these out of source control
DB_USER = "webapp"
DB_PASS = "Wint3rGarden!99"
API_KEY = "PENTESTTV{secrets_live_forever_in_git_history}"
EOF
git add -A && git commit -q -m "initial app and config"

# Commit 2: CI pipeline with hardcoded deploy credentials.
cat > Jenkinsfile <<'EOF'
pipeline {
  agent any
  environment {
    DEPLOY_USER = 'deploy'
    DEPLOY_PASS = 'D3ployP@ss2024'
    REGISTRY    = 'registry.pentesttv.local'
  }
  stages {
    stage('deploy') {
      steps { sh 'echo deploying as $DEPLOY_USER to $REGISTRY' }
    }
  }
}
EOF
git add -A && git commit -q -m "add CI deploy pipeline"

# Commit 3: "fix" by moving secrets to env vars (they remain in history).
cat > config.py <<'EOF'
import os
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
API_KEY = os.environ["API_KEY"]
EOF
git add -A && git commit -q -m "move secrets to environment variables"

# Publish as a dumb-HTTP-cloneable bare repo.
mkdir -p /srv/git
git clone -q --bare /build/webapp /srv/git/webapp.git
cd /srv/git/webapp.git
git update-server-info
rm -rf /build
echo "git repo published at /srv/git/webapp.git"
