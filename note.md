# Dev Notes

## Build a Docker image of Ubuntu with Python and Flask

```Dockerfile
FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y python3 \
                        python3-dev \
                        python3-pip \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

RUN export LC_ALL=C.UTF-8 \
    && export LANG=C.UTF-8

RUN pip3 install Flask -i https://pypi.doubanio.com/simple

CMD ["/bin/bash"]
```

```bash
$ docker build -t ubuntu-with-python:dev .
```

## Update the Docker image of Dev Env

```bash
$ docker ps
CONTAINER ID        IMAGE                            COMMAND             CREATED             STATUS              PORTS                    NAMES
9c1f1d3e7927        ubuntu-with-python:dev   "/bin/bash"         8 minutes ago       Up 8 minutes                            pensive_hofstadter
$ docker commit 9c1f1d3e7927 nld-sgn-env:dev
```

## Initiate Dev Env Docker

```bash
docker run -it --rm -v /c/Users/Benny/Documents/Projects/nld_sgn:/nld_sgn -p 80:80 ubuntu-with-python:dev /bin/bash
```