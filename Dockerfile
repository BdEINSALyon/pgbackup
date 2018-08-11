FROM python:3

RUN apt-get update -y && apt-get dist-upgrade -y && apt-get autoremove --purge -y && apt-get autoclean -y

RUN wget https://get.enterprisedb.com/postgresql/postgresql-10.4-1-linux-x64-binaries.tar.gz &&\
    tar xf postgresql-10.4-1-linux-x64-binaries.tar.gz &&\
    rm -rf postgresql-10.4-1-linux-x64-binaries.tar.gz pgsql/pgAdmin\ 4

RUN wget https://launchpadlibrarian.net/358695615/duplicity-0.7.17.tar.gz &&\
    tar xf duplicity-0.7.17.tar.gz &&\
    rm -rf duplicity-0.7.17.tar.gz &&\
    mv duplicity-0.7.17 duplicity

WORKDIR /backup

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PG_DUMP_COMMAND /pgsql/bin/pg_dump
ENV DATABASE_URL postgres://postgres@localhost/postgres
ENV FTP_URL ftp://backup:password@backup.network/backups/mydb
ENV DUPLICITY_COMMAND /duplicity/bin/duplicity
VOLUME /tmp

COPY backup.py .
CMD python /backup/backup.py
