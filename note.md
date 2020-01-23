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

## Initiate Dev Env Docker

```bash
$ docker run -it --rm -v /c/Users/Benny/Documents/Projects/nld_sgn:/nld_sgn -p 80:80 nld-sgn-env:pg /bin/bash
$ service nginx start
$ service redis-server start
$ cd /nld_sgn/app
$ nohup celery worker -A main.celery --loglevel=info >> celery.log &
$ # python main.py
$ gunicorn main:app --bind 0.0.0.0:8000 --workers 4 --log-level debug
```

## Build NEURO-LEARNN-DOCKER-SGN with Dev Env Docker

```Dockerfile
FROM nld-sgn-env:pg

ADD ./app/ /nld_sgn/
ADD ./start.sh /nld_sgn/

CMD ["sh","/nld_sgn/start.sh"]
```

## Initiate NLD-SGN

- Mount host directories into container in order to add writable files, such as new models.
```bash
$ docker run -it --rm -v /path/to/extra:/nld_sgn/extra -p 80:80 raniac/neuro-learn-docker:sgn
```

## References
- [Train and Deploy Machine Learning Model With Web Interface - PyTorch & Flask](https://imadelhanafi.com/posts/train_deploy_ml_model/)
- [在服务器的docker中部署深度学习模型（flask框架）](https://blog.csdn.net/MissShihong/article/details/103313396)

## Appendix

### Configuration of Nginx server
```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
        worker_connections 768;
        # multi_accept on;
}

http {
server {
    listen 80;
    server_name 0.0.0.0;
    charset UTF-8;

    access_log  /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    location / {
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

        ##
        # Basic Settings
        ##

        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;

        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings
        ##

        gzip on;
        gzip_disable "msie6";

        # gzip_vary on;
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k;
        # gzip_http_version 1.1;
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        ##
        # Virtual Host Configs
        ##

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
}


#mail {
#       # See sample authentication script at:
#       # http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
# 
#       # auth_http localhost/auth.php;
#       # pop3_capabilities "TOP" "USER";
#       # imap_capabilities "IMAP4rev1" "UIDPLUS";
# 
#       server {
#               listen     localhost:110;
#               protocol   pop3;
#               proxy      on;
#       }
# 
#       server {
#               listen     localhost:143;
#               protocol   imap;
#               proxy      on;
#       }
#}
```