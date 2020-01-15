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

## Create and Update the Docker image of Dev Env

### Create

```Dockerfile
FROM ubuntu-with-python:dev

RUN apt-get update \
    && apt-get install redis-server

RUN pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple

CMD ["/bin/bash"]
```

```bash
$ docker build -t nld-sgn-env:dev .
```

### Update

```bash
$ docker ps
CONTAINER ID        IMAGE                            COMMAND             CREATED             STATUS              PORTS                    NAMES
9c1f1d3e7927        nld-sgn-env:dev   "/bin/bash"         8 minutes ago       Up 8 minutes                            pensive_hofstadter
$ docker commit 9c1f1d3e7927 nld-sgn-env:dev
```

## Build Dev Env Docker from imcomking/pytorch_geometric:latest

```Dockerfile
FROM imcomking/pytorch_geometric:latest

RUN apt-get update \
    && apt-get -y install redis-server \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

ADD . /workspace/

RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple

CMD ["/bin/bash"]
```

```bash
$ cd env/nld-sgn-env/
$ docker build -t nld-sgn-env:pg .
```

## Initiate Dev Env Docker

```bash
$ docker run -it --rm -v /c/Users/Benny/Documents/Projects/nld_sgn:/nld_sgn -p 80:80 nld-sgn-env:pg /bin/bash
$ redis-server &
$ cd /nld_sgn/app
$ nohup celery worker -A main.celery --loglevel=info >> celery.log &
$ python main.py
```