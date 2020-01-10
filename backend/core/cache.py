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

    async def check_cache(self, report_id: str, character: str, boss_names):
        if not boss_names:
            return {'matches': await self.get_report_results(report_id, character), 'missing': []}
        key = f'{report_id}:{character}'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
                                                            
        cached_data = await __redis.smembers(key, encoding='utf-8')
        matches = {k: v for d in cached_data for k, v in ujson.loads(d).items() if k in boss_names}
        missing = list(set(boss_names) - set(matches.keys())) or []
        return {'matches': matches, 'missing': missing}