FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y python3 \
                        python3-dev \
                        python3-pip \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /nld_sgn
ADD . /nld_sgn/

# RUN cp -f /neuro-learn/nginx.conf /etc/nginx
RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple

CMD ["/bin/bash"]