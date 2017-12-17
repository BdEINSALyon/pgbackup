FROM python:3.6

RUN wget https://get.enterprisedb.com/postgresql/postgresql-10.1-3-linux-x64-binaries.tar.gz &&\
    tar xf postgresql-10.1-3-linux-x64-binaries.tar.gz &&\
    rm -rf postgresql-10.1-3-linux-x64-binaries.tar.gz pgsql/pgAdmin\ 4

WORKDIR /backup

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PG_DUMP_COMMAND /pgsql/bin/pg_dump
ENV DATABASE_URL postgres://postgres@localhost/postgres
ENV FTP_URL ftp://backup:password@backup.network/backups/mydb
VOLUME /tmp

COPY backup.py .
CMD python /backup/backup.py
