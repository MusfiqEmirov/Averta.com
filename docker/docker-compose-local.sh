#!/bin/bash
# Helper script for running local docker-compose
# Usage: ./docker-compose-local.sh up
#        ./docker-compose-local.sh down
#        ./docker-compose-local.sh build
#        etc.

if [ -z "$1" ]; then
    echo "Usage: ./docker-compose-local.sh [command]"
    echo "Example: ./docker-compose-local.sh up"
    exit 1
fi

docker-compose -f docker-compose-local.yaml "$@"

