from __future__ import unicode_literals, print_function, division
from database import execute, list

def clear_all():
    tables = _get_all_tables_and_views()
    for table in tables:
        _drop(table.type, table.name)
    _clear_all_migration_records()

def _get_all_tables_and_views():
    return list("""
        SELECT table_name as name, 'table' as type FROM information_schema.tables
          WHERE table_schema='lvye_pay' AND table_type='base table';
    """)

def _drop(type, name):
    if type == 'table':
        _drop_table(name)
    elif type == 'view':
        _drop_view(name)

def _drop_table(table_name):
    if table_name != 'migrate_command_center':
        print("[CLEAR ALL] - Drop table", table_name)
        execute("DROP TABLE %s CASCADE" % table_name)

def _drop_view(view_name):
    print('[CLEAR ALL] - Drop view', view_name)
    execute('DROP VIEW %s' % view_name)

def _clear_all_migration_records():
    print("[CLEAR ALL] - Clear migration records")
    try:
        execute('TRUNCATE TABLE migrate_command_center')
    except:
        pass

if __name__ == '__main__':
    clear_all()
