import pymysql
import sys
import yaml
from urllib.parse import urlparse


def execute(conn, stmt):
    cur = conn.cursor()
    cur.execute(stmt)
    fields = [r[0] for r in cur.description]
    rows = [dict(zip(fields, row)) for row in cur]
    cur.close()
    return rows


def load_data(url):
    conn = pymysql.connect(
        host=url.hostname,
        port=url.port or 3306,
        user=url.username,
        passwd=url.password,
        db=url.path[1:])
    fields = execute(conn, """
        SELECT table_schema,
               table_name,
               column_name,
               data_type,
               character_maximum_length,
               extra
        FROM columns
        WHERE table_schema NOT IN ('information_schema',
                                   'mysql',
                                   'performance_schema',
                                   'sys')
    """)
    constraints = execute(conn, """
        SELECT table_name,
               column_name,
               constraint_name,
               referenced_table_name,
               referenced_column_name
        FROM information_schema.key_column_usage
        WHERE referenced_table_schema NOT IN ('information_schema',
                                              'mysql',
                                              'performance_schema',
                                              'sys')
    """)
    conn.close()
    return {'fields': fields,
            'constraints': constraints}


def main(url, databases):
    data = load_data(urlparse(url))
    constraints = dict([(r['column_name'],
                         (r['referenced_table_name'],
                          r['referenced_column_name']))
                        for r in data['constraints']])
    schema = {}
    for row in data['fields']:
        if databases and row['table_schema'] not in databases:
            continue
        if row['table_schema'] not in schema:
            schema[row['table_schema']] = {}
        if row['table_name'] not in schema[row['table_schema']]:
            schema[row['table_schema']][row['table_name']] = {
                '__meta__': {'count': 10}}
        table = schema[row['table_schema']][row['table_name']]
        if row['column_name'] in constraints:
            value = 'ref("%s", "%s")' % constraints[row['column_name']]
        elif row['data_type'] in (
                'tinyint', 'smallint', 'bigint',
                'int', 'float', 'double', 'decimal'):
            value = 'auto_increment(100)'
        elif row['data_type'] in ('varchar', 'char'):
            value = 'random_name(%s)' % row['character_maximum_length']
        elif row['data_type'] == 'datetime':
            value = '"2018-03-21 16:48:17"'
        elif row['data_type'] == 'time':
            value = '"16:48:17"'
        elif row['data_type'] in ('text', 'mediumtext', 'longtext'):
            value = 'random_name(512)'
        else:
            value = ''
        table[row['column_name']] = value
    return schema


if __name__ == '__main__':
    db_url = sys.argv[1]
    databases = [] if len(sys.argv) < 3 else sys.argv[2].split(',')
    print(yaml.dump(main(db_url, databases)))
