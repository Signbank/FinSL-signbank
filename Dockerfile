FROM python:3.11-slim-bookworm

RUN apt update && export DEBIAN_FRONTEND=noninteractive && apt upgrade -y && apt install -y gettext git

WORKDIR /usr/src/app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt requirements_os.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements_os.txt

COPY . .

RUN python bin/openshift.py compilemessages

USER nobody:0

EXPOSE 8080

ENTRYPOINT ["./docker-entrypoint.sh"]