import random
import string
import sys

from toposort import toposort_flatten
import yaml


AUTO_INCREMENTS = {}
DB = None
TABLE = None
FIELD = None
REFS = {}


def ref(table, column):
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
    global DB, TABLE, FIELD
    meta = get_meta(schema, db, table)
    fields = get_fields(schema, db, table)
    rows = [list(fields.keys())]
    for n in range(meta['count']):
        row = []
        for field, value in fields.items():
            if value and isinstance(value, str):
                DB, TABLE, FIELD = db, table, field
                value = eval(value)
                DB, TABLE, FIELD = None, None, None
            row.append(value)
        rows.append(row)
    return rows


def get_databases(schema):
    return schema.keys()


def get_tables(schema, db):
    return schema[db].keys()


def get_fields(schema, db, table):
    return dict([(k, v) for k, v in schema[db][table].items()
                 if k != '__meta__'])


def get_meta(schema, db, table):
    return schema[db][table]['__meta__']


def get_tables_order(schema, db):
    deps = {}
    _ref = lambda t, c: deps[table].add(t)  # noqa
    for table in get_tables(schema, db):
        deps[table] = set()
        for field, value in get_fields(schema, db, table).items():
            if value and isinstance(value, str) and 'ref(' in value:
                eval('_' + value)
    return toposort_flatten(deps)


def main(schema):
    orders = {}
    for db in get_databases(schema):
        orders[db] = get_tables_order(schema, db)
        for table in orders[db]:
            rows = generate_table_rows(schema, db, table)
            REFS[(db, table)] = rows
            print('table %s' % table)
            print(rows)


if __name__ == '__main__':
    main(yaml.safe_load(open(sys.argv[1])))
