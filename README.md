# Fields2Cover REST API

Simple REST API using Python's FastAPI for path planning with Fields2Cover.

## Installation via Docker (recommended)

> *NOTE: These instructions are Windows-centric. If not using Windows, install Docker via package manager of choice, pull the image down from Docker Hub, and start it in daemon mode.*

- [Install WSL2](https://learn.microsoft.com/en-us/windows/wsl/install). Recommend using an Ubuntu LTS distribution as the default.
- [Install Docker Desktop](https://docs.docker.com/desktop/features/wsl/) and ensure Docker support for WSL2 is enabled.

- Open a WSL terminal and issue:
```
sudo apt update && sudo apt upgrade -y
docker pull yurirage/f2c-rest-api:latest
```

- To test on port 8087:
```
docker run -p 8087:8000 --name f2c yurirage/f2c-rest-api:latest
```

- To automatically start and restart on failure:
```
docker run -d --restart unless-stopped -p 8087:8000 --name f2c yurirage/f2c-rest-api:latest
```

- To confirm the API is running and see version information, open http://localhost:8087 in a web browser.

## Updating

- To use the latest Docker image when an update is released, open a WSL terminal and issue the following:
```
docker pull yurirage/f2c-rest-api:latest
docker stop f2c && docker rm f2c
docker run -d --restart unless-stopped -p 8087:8000 --name f2c yurirage/f2c-rest-api:latest

```

# Alternate API Hosting Methods:

If you don't want to use Docker, or you prefer to build the image for yourself rather than pulling from Docker Hub, the following methods can be used.

## Clone and run locally

If you want to run without Docker, clone the repo and run with Python. You will need a local installation of [Fields2Cover](https://github.com/Fields2Cover/Fields2Cover) built with Python bindings and associated dependencies. Once dependencies are satisfied:

```
git clone https://github.com/yuri-rage/f2c-rest-api.git
cd f2c-rest-api
./run.py
```

## Build Docker container locally

Install Docker and the BuildKit plugin (`sudo apt install docker-buildx` or `yay -S docker-buildx`). Then:
```
export DOCKER_BUILDKIT=1
docker buildx build -t f2c-rest-api .
docker run -p 8087:8000 --name f2c f2c-rest-api:latest
```
