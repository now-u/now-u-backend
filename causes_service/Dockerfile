FROM python:3.14.3-slim-trixie

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update -y && \
    apt-get install -y build-essential netcat-openbsd xmlsec1 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install gunicorn

COPY ./app_links/generated_client/requirements.txt /app/app_links/generated_client/requirements.txt
RUN pip install -r /app/app_links/generated_client/requirements.txt

COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

COPY . .

WORKDIR /app/app_links/generated_client
RUN python setup.py install
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
