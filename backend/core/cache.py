import asyncio
import aioredis
import datetime
import ujson
import os

class RedisClient:

    def __init__(self, *args, **kwargs):
        self.redis_host = os.getenv('CACHE_HOST')

    async def get_report_results(self, report_id: str, character: str):
        key = f'{report_id}:{character}'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
                                                            
        cached_data = await __redis.smembers(key, encoding='utf-8')
        return {k: v for d in cached_data for k, v in ujson.loads(d).items()}

    async def save_results(self, report_id: str, character: str, data):
        key = f'{report_id}:{character}'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        d = await __redis.sadd(key, *[ujson.dumps({k: v}) for k, v in data.items()])
        __redis.close()
        return d
