import logging

import dj_database_url
import configargparse
from datetime import datetime
from sultan.api import Sultan
from urllib import parse as urlparse
import ftputil

root = logging.getLogger()
root.setLevel(logging.INFO)

p = configargparse.ArgumentParser()
p.add('--db', required=True, help='database url (e.g. postgres://postgres@localhost/db)',
      env_var='DATABASE_URL')
p.add('--ftp', required=True, help='FTP url (e.g. ftp://backup:password@backup.network/backups/mydb)',
      env_var='FTP_URL')
p.add('--pgdump', required=False, help='pg_dump path command',
      env_var='PG_DUMP_COMMAND', default='pg_dump')
p.add('--max', required=False, help='maximum count of backups',
      env_var='MAX_FILES', default=5)
p.add('--name', required=False, help='backup name',
      env_var='BACKUP_NAME', default='manual_backup')
options = p.parse_args()

s = Sultan()


def backup_front_name(database):
    db = dj_database_url.parse(database)
    return db['HOST'] + '-' + db['NAME'] + '-' + options.name


def backup_name(database):
    now = datetime.now()
    now = now.replace(microsecond=0)
    return backup_front_name(database) + '-' + now.isoformat() + ".psql"


def backup(database, ftp, pgdump):
    logging.info('Starting backup')
    name = backup_name(database)
    path = '/tmp/' + name
    logging.info('Backup database to {}'.format(path))
    s.bash('-c', '"'+' '.join([pgdump, '-d', database]) + '"').redirect(
        path,
        append=False,
        stdout=True,
        stderr=False).run()

    s.tar('cf', path + '.tar.gz', path).run()

    s.rm(path).run()

    path = path + '.tar.gz'

    ftp = urlparse.urlparse(ftp, 'ftp')
    logging.info('Sending backup {} to {}'.format(path, ftp.hostname))

    host = ftp.hostname
    if ftp.port:
        host = host + ':' + ftp.port

    # noinspection is due to an error into FTPHost code
    # noinspection PyDeprecation
    with ftputil.FTPHost(host, ftp.username, ftp.password) as host:
        host.makedirs(ftp.path)
        host.upload_if_newer(path, ftp.path + name + '.tar.gz')
        host.chdir(ftp.path)
        files = [file for file in host.listdir(ftp.path) if file.startswith(backup_front_name(database))]
        files.sort()
        while len(files) > options.max:
            old_file = files.pop(0)
            host.remove(ftp.path + old_file)
            logging.info("Deleted old file {}".format(old_file))

    s.rm(path).run()
    logging.info('Ended')


if __name__ == '__main__':
    backup(options.db, options.ftp, options.pgdump)
