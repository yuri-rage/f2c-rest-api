# Fields2Cover REST API

Simple REST API using Python's FastAPI for path planning with Fields2Cover.

## Installation via Docker (recommended)

- [Install WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) (if using Windows)
- Open terminal and issue:
```
sudo apt update && sudo apt upgrade -y
sudo apt install docker
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

## Clone and run locally

If you want to run without Docker, clone the repo and run with Python. You will need a locally installation of [Fields2Cover](https://github.com/Fields2Cover/Fields2Cover) built with Python bindings and associated dependencies. Once dependencies are satisfied:

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

