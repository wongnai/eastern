FROM python:3.6-stretch

RUN wget -O /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v1.8.4/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl

COPY . /app/
RUN cd /app/ \
    && python setup.py install \
    && rm -rf /app/

CMD ["eastern"]
