import os
from superset.config import *
from werkzeug.contrib.cache import RedisCache


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = 'The environment variable {} was missing, abort...' \
                .format(var_name)
            raise EnvironmentError(error_msg)

invocation_type = get_env_variable('INVOCATION_TYPE')
if invocation_type in ('COMPOSE', 'K8S'):
    MYSQL_USER = get_env_variable('MYSQL_USER')
    MYSQL_PASS = get_env_variable('MYSQL_PASS')
    MYSQL_HOST = get_env_variable('MYSQL_HOST')
    MYSQL_PORT = get_env_variable('MYSQL_PORT')
    MYSQL_DATABASE = get_env_variable('MYSQL_DATABASE')

    # The SQLAlchemy connection string.
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER,
                                                          MYSQL_PASS,
                                                          MYSQL_HOST,
                                                          MYSQL_PORT,
                                                          MYSQL_DATABASE)
elif invocation_type == 'RUN':
    SQLALCHEMY_DATABASE_URI = get_env_variable('DB_URL')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'superset.db')

REDIS_HOST=''
REDIS_PORT=''
REDIS_DB=0

if invocation_type in ('COMPOSE', 'K8S'):
    REDIS_HOST = get_env_variable('REDIS_HOST')
    REDIS_PORT = get_env_variable('REDIS_PORT')
    REDIS_DB = int(get_env_variable('REDIS_DB'))
    RESULTS_BACKEND = RedisCache(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, key_prefix='superset_results')
elif invocation_type == 'RUN':
    REDIS_HOST = get_env_variable('REDIS_URL').split(":")[1].replace("/","")
    REDIS_PORT = get_env_variable('REDIS_URL').split(":")[2].replace("/0","")
    RESULTS_BACKEND = RedisCache(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, key_prefix='superset_results')
else:
    RESULTS_BACKEND = None


CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24, # 1 day default (in secs)
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': 'redis://%s:%s/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB),
}

TABLE_NAMES_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24, # 1 day default (in secs)
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': 'redis://%s:%s/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB),
}

class CeleryConfig(object):
    BROKER_URL = ('redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT), 'sqla+sqlite:///'+ os.path.join(DATA_DIR, 'celeryDB.db'))[bool(not REDIS_HOST)]
    CELERY_RESULT_BACKEND = ('redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT), 'db+sqlite:///'+ os.path.join(DATA_DIR, 'celeryResultDB.db'))[bool(not REDIS_HOST)]
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig
