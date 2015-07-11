from paver.easy import *
from paver.setuputils import setup

# setup(
#         name="lvye-zyt",
#         packages=['cc'],
#         version="1.0",
#         )
#
# @task
# def build_dep(options):
#     sh('pip install -q -r dependencies.txt')

@task
def migrate(options):
    sh('python migrate/lib/migrate.py migrate/schema')

@task
def reset_all(options):
    clear_all(options)
    migrate(options)

@task
def clear_all(options):
    sh('python migrate/lib/clear_all.py')

