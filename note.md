# Dev Note

## Design

### Overview

This project aims to containerize/dockerize Schizo_Graph_Net as a service of NEURO-LEARN, developed with Flask.
- Expose new_task api so as to create new deep learning task utilizing SGN;
- SGN is developed with Pytorch and Pytorch_Geometric;
- Include Train-From-Scratch and Fine-Tune(use trained-model parameters);
- Incorporate DAO in order to perform CRUD on database, including insert_new_task, update_task_result, get_data, and get_model;
- Use Celery for queued task execution, along with Redis as cache backend;
- As for deployment, utilize Nginx as Reverse Proxy and Gunicorn as Load Balancing;
- Local deployment and container management are realized with docker-compose;
- Clustered computing services are implemented by kubernetes;

### API Definition

#### New Task
- Request Information
  - Address: ```/api/v0/new_task```
  - Method: POST
- Response Information
  - Type: HTTP
  - Content:
    - ```error_num```: request status
    - ```msg```: request result
    - ```task_form```: task form info
- Parameter Definition:

Parameter Name | Description | Necessary | Type | Default Value
:-: | :-: | :-: | :-: | :-:
```task_name``` | Task Name | True | STRING |
```task_type``` | Task Type | True | STRING |
```proj_id``` | Project ID | True | STRING |
```proj_name``` | Task Name | True | STRING |
```train_data``` | Train Data | True | STRING |
```val_data``` | Train Data | True | STRING |
```enable_test``` | Enable Test | True | BOOLEAN |
```test_data``` | Test Data | True | STRING |
```model``` | Model | True | STRING |
```param_set:learning_rate``` | Learning Rate | True | STRING |
```param_set:batch_size``` | Batch Size | True | STRING |
```param_set:lr_step_size``` | LR Step Size | True | STRING |
```param_set:lr_decay``` | LR Decay | True | STRING |
```param_set:epochs``` | Epochs | True | STRING |
```param_set:trained_task_id``` | Trained Task ID | True | STRING |

- POST Form Example

```json
{
    "proj_id":"PROJ20191217104136",
	"proj_name":"SZ with sfMRI",
	"task_name":"test",
	"task_type":"dl_ft",
	"train_data":["A_181210_140_SZ_sfMRI_AAL90"],
	"val_data":["A_181210_140_SZ_sfMRI_AAL90"],
	"enable_test":true,
	"test_data":["A_181210_140_SZ_sfMRI_AAL90"],
	"model":"GNN",
	"param_set": {
	    "learning_rate": 5e-2,
	    "batch_size": 10,
	    "lr_step_size": 60,
	    "lr_decay": 0.2,
	    "epochs": 1,
	    "trained_task_id": "TASK20012912454500"
	}
}
```

## Development

### Build a Docker image of Ubuntu with Python and Flask

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

### Create and Update the Docker image of Dev Env

#### Create

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

#### Update

```bash
$ docker ps
CONTAINER ID        IMAGE                            COMMAND             CREATED             STATUS              PORTS                    NAMES
9c1f1d3e7927        nld-sgn-env:dev   "/bin/bash"         8 minutes ago       Up 8 minutes                            pensive_hofstadter
$ docker commit 9c1f1d3e7927 nld-sgn-env:dev
```

### Build Dev Env Docker from imcomking/pytorch_geometric:latest

```Dockerfile
FROM imcomking/pytorch_geometric:latest

RUN apt-get update \
    && apt-get -y install nginx \
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

### Initiate Dev Env Container

```bash
$ docker run -it --rm -v /c/Users/Benny/Documents/Projects/nld_sgn:/nld_sgn -p 80:80 nld-sgn-env:pg /bin/bash
$ # service nginx start
$ service redis-server start
$ cd /nld_sgn/app
$ nohup celery worker -A main.celery --loglevel=info >> celery.log &
$ python main.py
$ # gunicorn main:app --bind 0.0.0.0:8000 --workers 4 --log-level debug
```

## Deployment

### Build Docker Registry for Kubernetes

#### Server End

```bash
$ docker search registry
$ docker run -d -p 5000:5000 -v /docker/registry/data:/var/lib/registry --privileged=true --restart=always --name registry registry:latest
```

> Note that the port 5000 of the server need to be opened.

#### User End

- Ubuntu: configure ```"insecure-registries"``` in ```/etc/docker/daemon.json```;
- Windows: configure ```"insecure-registries"``` in Daemon of Docker Desktop.

```bash
$ docker tag ubuntu-with-python:dev 120.79.49.129:5000/ubuntu-with-python:latest
$ docker push 120.79.49.129:5000/ubuntu-with-python
```

### Build NEURO-LEARNN-DOCKER-SGN with Dev Env Docker

```Dockerfile
FROM nld-sgn-env:pg

ADD . /nld_sgn/

CMD ["sh","/nld_sgn/start.sh"]
```

> Use .dockerignore to neglect useless files.

### Initiate NLD-SGN container

- Mount host directories into container in order to add writable files, such as new models.
```bash
$ docker run -it --rm -v /path/to/models:/nld_sgn/models -p 80:80 raniac/neuro-learn-docker:sgn
```
- Or use docker-compose.

### Use Docker-Compose to Deploy Containerized Services

```yml
version: '2'

services:
  sgn-service:
    image: 120.79.49.129:5000/neuro-learn-docker:sgn
    restart: on-failure
    hostname: sgn-server
    ports:
      - "80:80"
    volumes:
      - /c/Users/Benny/Documents/Projects/nld_sgn/models:/nld_sgn/models
    # environment:
    #   KAFKA_ADVERTISED_HOST_NAME: localhost
    # depends_on:
    #   - zoo1
    container_name: sgn-service
```

## References
- [Train and Deploy Machine Learning Model With Web Interface - PyTorch & Flask](https://imadelhanafi.com/posts/train_deploy_ml_model/)
- [在服务器的docker中部署深度学习模型（flask框架）](https://blog.csdn.net/MissShihong/article/details/103313396)
- [关于docker-Compose基本使用](https://www.jianshu.com/p/808385b9e4aa)
- [Flask 应用如何部署](https://www.cnblogs.com/hellohorld/p/10033720.html)
- [Docker+K8S笔记(二)：Linux安装docker-registry](https://my.oschina.net/u/4075242/blog/3068384)

## Appendix

### Nginx Configuration

See nginx.conf.

### Docker-Compose Configuration

See docker-compose.yml.