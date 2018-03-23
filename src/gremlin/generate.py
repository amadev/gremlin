import csv
import os
import random
import string
import shutil
import sys

from toposort import toposort_flatten
import yaml


AUTO_INCREMENTS = {}
DB = None
TABLE = None
FIELD = None
REFS = {}
ROWS = None
ROW = None


def ref(table, column):
    # self reference case
    if table == TABLE:
        ind = ROWS[0].index(column)
        if len(ROWS) > 1:
            r = random.choice(ROWS[1:])[ind]
        else:
            r = ROW[ind]
        return r
    ref_table = REFS[(DB, table)]
    ind = ref_table[0].index(column)
    return random.choice(ref_table[1:])[ind]


def auto_increment(value):
    path = (DB, TABLE, FIELD)
    if path not in AUTO_INCREMENTS:
        AUTO_INCREMENTS[path] = value
    else:
        AUTO_INCREMENTS[path] += 1
    return AUTO_INCREMENTS[path]


def random_name(N):
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(N))


def generate_table_rows(schema, db, table):
    global DB, TABLE, FIELD, ROWS, ROW
    meta = get_meta(schema, db, table)
    fields = get_fields(schema, db, table)
    rows = [[k for k, v in fields]]
    for n in range(meta['count']):
        row = []
        for field, value in fields:
            if value and isinstance(value, str):
                DB, TABLE, FIELD, ROWS, ROW = db, table, field, rows, row
                value = eval(value)
                DB, TABLE, FIELD, ROWS, ROW = None, None, None, None, None
            row.append(value)
        rows.append(row)
    return rows


def get_databases(schema):
    return schema.keys()


def get_tables(schema, db):
    return schema[db].keys()


def get_fields(schema, db, table):
    return [(k, v) for k, v in sorted(
        schema[db][table].items(),
        key=lambda x: (1, x) if 'ref(' in x[0] else (0, x))
            if k != '__meta__']


def get_meta(schema, db, table):
    return schema[db][table]['__meta__']


def get_tables_order(schema, db):
    deps = {}
    _ref = lambda t, c: deps[table].add(t)  # noqa
    for table in get_tables(schema, db):
        deps[table] = set()
        for field, value in get_fields(schema, db, table):
            if value and isinstance(value, str) and 'ref(' in value:
                eval('_' + value)
    return toposort_flatten(deps)


def main(schema):
    shutil.rmtree('.build', ignore_errors=True)
    orders = {}
    for db in get_databases(schema):
        path = '.build/%s' % db
        os.makedirs(path)
        orders[db] = get_tables_order(schema, db)
        for table in orders[db]:
            rows = generate_table_rows(schema, db, table)
            REFS[(db, table)] = rows
            with open('%s/%s' % (path, table), 'w') as f:
                writer = csv.writer(f,
                                    delimiter=';',
                                    lineterminator='\r\n',
                                    quoting=csv.QUOTE_ALL,
                                    quotechar='"')
                writer.writerows(rows)
            with open('%s/%s' % (path, '.order'), 'w') as f:
                f.write(' '.join(orders[db]))


if __name__ == '__main__':
    main(yaml.safe_load(open(sys.argv[1])))
