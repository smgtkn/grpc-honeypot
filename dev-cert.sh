#!/usr/bin/env bash
set -euo pipefail

# Simple helper to create a self-signed cert and key for local testing
# Outputs: server.crt and server.key in current directory

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout server.key -out server.crt -days 365 \
  -subj "/C=US/ST=State/L=City/O=Org/OU=Dev/CN=localhost"

echo "Generated server.crt and server.key"
