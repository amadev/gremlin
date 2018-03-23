import csv
import os
from urllib.parse import urlparse
import subprocess
import sys


def main(url):
    path = '.build'
    for db in os.listdir(path):
        with open('%s/%s/.order' % (path, db)) as f:
            files = ['%s/%s/%s' % (path, db, name)
                     for name in f.read().strip().split()]

        for fpath in files:
            with open(fpath) as f:
                r = csv.reader(f,
                               delimiter=';',
                               lineterminator='\r\n',
                               quoting=csv.QUOTE_ALL,
                               quotechar='"')
                columns = next(r)
            cmd = ('mysqlimport '
                   '--fields-terminated-by ";" '
                   "--fields-enclosed-by '\"' "
                   '--lines-terminated-by "\r\n" '
                   '--local '
                   '--ignore-lines 1 '
                   '--columns %(columns)s '
                   '-u %(user)s -h %(host)s -p%(pass)s '
                   '%(db)s '
                   '%(path)s') % {
                       'user': url.username,
                       'host': url.hostname,
                       'pass': url.password,
                       'db': db,
                       'path': fpath,
                       'columns': ','.join(columns)}
            subprocess.check_call(cmd, shell=True)


if __name__ == '__main__':
    main(urlparse(sys.argv[1]))
