FROM nld-sgn-env:pg

ADD ./app/ /nld_sgn/
ADD ./start.sh /nld_sgn/

CMD ["sh","/nld_sgn/start.sh"]