FROM python:3.9 as server-build

RUN apt-get update && apt-get install -y libsasl2-dev libldap2-dev libssl-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
WORKDIR /server/
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./ /server/
RUN python manage.py collectstatic --noinput
