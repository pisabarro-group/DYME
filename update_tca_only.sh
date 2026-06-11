#!/usr/bin/env bash
#This file tells a running dyme_main node (locally) to update the frontend without rebooting

# Check if dyme_main container is running
CONTAINER_STATUS=$(docker inspect -f '{{.State.Running}}' dyme_main 2>/dev/null)

if [ "$CONTAINER_STATUS" != "true" ]; then
    echo "[ERROR] dyme_main container is not running. Aborting."
    exit 1
fi

echo "[INFO] Updating frontend inside container..."
docker exec dyme_main update_frontend.sh

echo "[INFO] Frontend updated. Please reload your browser window"