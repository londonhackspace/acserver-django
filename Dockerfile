FROM python:3.11 AS server-build

WORKDIR /server/
RUN apt-get update && apt-get install -y libsasl2-dev libldap2-dev libssl-dev && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY ./ /server/
RUN python manage.py collectstatic --noinput
CMD bash runserver.sh
