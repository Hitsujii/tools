#!/usr/bin/env bash

# Path to your public SSH key
PUBKEY="$HOME/.ssh/id_ed25519.pub"

# List of target hosts in the format: user@hostname port
# Replace the placeholders with actual values
read -r -d '' HOSTS <<EOF
user1@your-server.com  22
user2@another-server.net  2222
EOF

while read -r userhost port; do
  [[ -z "$userhost" ]] && continue  # skip empty lines or comments

  echo -e "\n===> Copying public key to $userhost (port $port)..."

  cat "$PUBKEY" | ssh -p "$port" "$userhost" \
    'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'

done <<< "$HOSTS"
