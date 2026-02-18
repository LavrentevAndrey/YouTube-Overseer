#!/bin/bash

# Safety Killswitch for YouTube Overseer
# Flushes the custom chain and removes the jump rule.

CHAIN_NAME="OVERSEER_BLOCK"

# Check if we are root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit 1
fi

echo "Disabling Overseer Network Block..."

# 1. Remove the jump rule from OUTPUT to OVERSEER_BLOCK
# check if it exists first to avoid error? iptables -C ...
if iptables -C OUTPUT -j $CHAIN_NAME 2>/dev/null; then
    iptables -D OUTPUT -j $CHAIN_NAME
    echo "Removed jump rule from OUTPUT."
else
    echo "Jump rule not found (already removed?)."
fi

# 2. Flush the custom chain
if iptables -L $CHAIN_NAME -n >/dev/null 2>&1; then
    iptables -F $CHAIN_NAME
    echo "Flushed $CHAIN_NAME chain."
    
    # 3. Delete the custom chain
    iptables -X $CHAIN_NAME
    echo "Deleted $CHAIN_NAME chain."
else
    echo "Chain $CHAIN_NAME not found."
fi

echo "Network restrictions lifted."
