import redis
import datetime
import ujson
import os

class RedisClient:

    def __init__(self, *args, **kwargs):
        redis_host = os.getenv('CACHE_HOST')
        self.__redis = redis.Redis(host=redis_host, port=6379, db=0)

    def get_report_results(self, report_id: str, character: str):
        key = f'{report_id}:{character}'
        cached_data = self.__redis.get(key)
        if not cached_data:
            return None
        return ujson.loads(cached_data)

    def save_results(self, report_id: str, character: str, data):
        key = f'{report_id}:{character}'
        return self.__redis.set(key, ujson.dumps(data))
