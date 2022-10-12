from flask_caching import Cache
from configure import conf

cache = Cache(config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_KEY_PREFIX': f'{conf["FLASK_CACHE_PREFIX"]}:',
        'CACHE_REDIS_URL': f'redis://{conf["CACHE_REDIS_NAME"]}:{conf["CACHE_REDIS_PASSWD"]}@'
                           f'{conf["CACHE_REDIS_HOST"]}:{conf["CACHE_REDIS_PORT"]}/{conf["CACHE_REDIS_DATABASE"]}'
    })
