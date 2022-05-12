FROM node:lts AS node

WORKDIR /app
ADD ./signbank/static signbank/static
ADD package.json /app

ADD package-lock.json /app

RUN npm ci &&\
    npm run collectjs &&\
    npm run collectcss

FROM python:3.9

CMD pip install -r requirements.txt && \
    python bin/develop.py migrate --noinput && \
    python bin/develop.py createcachetable && \
    python bin/develop.py loaddata signbank/contentpages/fixtures/flatpages_initial_data.json &&\
    python bin/develop.py createcachetable && \
    python bin/develop.py runserver 0.0.0.0:${PORT:=8000}

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN echo "APT::Install-Recommends \"0\";" >> /etc/apt/apt.conf.d/02recommends && \
    echo "APT::Install-Suggests \"0\";" >> /etc/apt/apt.conf.d/02recommends && \
    apt-get -qq update && \
    apt-get -qq install \
        build-essential \
        postgresql-client \
        && \
    rm -rf /var/lib/apt/lists/* && \
    true

# Install requirements
WORKDIR /app
ADD requirements.txt /app
RUN pip --no-cache-dir install --src=/opt pyinotify -r requirements.txt

# Copy frontend assets
COPY --from=node /app/signbank/static/js ./
COPY --from=node /app/signbank/static/css ./

# Install application
ADD . /app
