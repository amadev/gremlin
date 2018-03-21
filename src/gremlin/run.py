import csv
import os
import subprocess


def main():
    creds = '-utest -ptest'
    path = '.build'
    cmd = 'mysql %(creds)s --execute "drop database nova"' % {'creds': creds}
    subprocess.check_call(cmd, shell=True)
    cmd = 'mysql %(creds)s < src/gremlin/db.sql' % {'creds': creds}
    subprocess.check_call(cmd, shell=True)
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
                   '%(creds)s '
                   '%(db)s '
                   '%(path)s') % {
                       'creds': creds,
                       'db': db,
                       'path': fpath,
                       'columns': ','.join(columns)}
            subprocess.check_call(cmd, shell=True)


if __name__ == '__main__':
    main()
