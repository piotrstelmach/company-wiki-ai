#!/bin/bash

# Run tests inside the docker container
# The 'api' service in docker-compose has the backend mounted at /app

docker compose exec api env PYTHONPATH=. pytest tests
