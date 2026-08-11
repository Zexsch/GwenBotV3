#!/usr/bin/env bash

CONTAINER_NAME="gwenbot-test"

stopdocker() {
  docker stop "$CONTAINER_NAME" &>/dev/null
  exit 0
}

trap stopdocker SIGINT

# Starts the test bot locally. Needs docker installed.
docker run -d --rm -v "$CONTAINER_NAME"-data:/var/lib/mysql --name "$CONTAINER_NAME" -p 3307:3306 -e MYSQL_ROOT_PASSWORD=test -e MYSQL_DATABASE=gwenbot mysql:8

count=0
sleep_count=0
until [ "$count" -ge 2 ]; do
  echo "Waiting for MySQL to initialise. Time passed: $sleep_count s"
  count=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -c "ready for connections")
  sleep 1
  sleep_count=$(($sleep_count+1))
done

ENV_FILE=.env.dev uv run alembic upgrade head 
uv run --env-file .env.dev python src/gwenbotv3/main.py