FROM python:3.7-stretch
ENV PYTHONUNBUFFERED=true

RUN wget -O /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v1.11.1/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl

COPY . /app/
RUN cd /app/ \
    && python setup.py install \
    && rm -rf /app/

CMD ["eastern"]
