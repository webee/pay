from __future__ import unicode_literals, print_function, division
import glob
import database
import os
from paver.easy import sh

def migrate(script_path):
    migrate_table = 'migrate_command_center'
    print('Begin to migrate ...')
    print("Migrate table is '%s'" % migrate_table)
    try:
        database.execute(
            """
            CREATE TABLE %s(
                script_name VARCHAR(150) NOT NULL,
                success BOOLEAN NOT NULL DEFAULT TRUE,
                executed_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """ % migrate_table)
    except Exception as err:
        if 'already exists' not in str(err):
            raise
    error_script = database.scalar('SELECT script_name FROM %s WHERE success = FALSE' % migrate_table)
    if error_script:
        print("There is a failed script in last run: %s \nPlease make sure it is fixed." % error_script)
        database.execute('delete from ' + migrate_table + ' where success = False')
    executed = [rec.script_name for rec in database.list('SELECT script_name FROM %s' % migrate_table)]
    scripts = [script for script in glob.glob(os.path.join(script_path, '*.*'))]
    scripts.sort()
    for script in scripts:
        script_name = script[script.rfind('/') + 1:]
        if script_name not in executed:
            try:
                print('[MIGRATE] - execute: %s' % script_name)
                if script_name.endswith('.sql'):
                    database.execute(open(script, 'r').read())
                elif script_name.endswith('.py'):
                    sh('python %s' % script)
                else:
                    raise Exception('Unsupported migrate script: %s' % script_name)
            except Exception as ex:
                print('Error to execute script %s' % script_name)
                database.execute('INSERT INTO ' + migrate_table + '(script_name, success) VALUES(%s, FALSE)',
                                 (script_name,))
                raise
            database.execute('INSERT INTO ' + migrate_table + '(script_name) VALUES(%s)', (script_name,))
    print('System is up to date')

if __name__ == '__main__':
    migrate('migrate/schema')

