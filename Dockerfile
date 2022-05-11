FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED=true

RUN wget -O /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v1.24.0/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl

COPY . /app/
RUN cd /app/ \
    && python setup.py install \
    && rm -rf /app/

CMD ["eastern"]
