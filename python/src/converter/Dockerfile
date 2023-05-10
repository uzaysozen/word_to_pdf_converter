FROM python:3.10-slim-bullseye
RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential python3-uno libreoffice-script-provider-python unoconv libreoffice \
    && pip install --no-cache-dir --upgrade pip

RUN sed -i 's|#!/usr/bin/env python3|#!/usr/bin/python3|' /usr/bin/unoconv

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

CMD ["python3", "consumer.py"]
