import asyncio
import aioredis
import datetime
import ujson
import os

class RedisClient:

    def __init__(self, *args, **kwargs):
        self.redis_host = os.getenv('CACHE_HOST') or '0.0.0.0'

    async def get_report_results(self, report_id: str, character: str):
        key = f'{report_id}:{character}*'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        keys = await __redis.keys(key, encoding='utf-8')                                  
        cached_data = [dict(await __redis.hgetall(key, encoding='utf-8')) for key in keys]
        resp = {d.get('boss_name'): d for d in cached_data}
        return resp
    

    async def save_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        d = []
        for k, v in data.items():
            key = f'{report_id}:{character}:{k}'
            v['t1_set'] = str(v.get('t1_set'))
            v['no_d_stance'] = ujson.dumps(v.get('no_d_stance'))
            r = await __redis.hmset_dict(key, v)
            d.append(r)
        __redis.close()
        return d

    async def check_cache(self, report_id: str, character: str, boss_names):
        if not boss_names:
            return {'matches': await self.get_report_results(report_id, character), 'missing': []}
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
                                                            
        cached_data = [dict(await __redis.hgetall(f'{report_id}:{character}:{b}', encoding='utf-8')) for b in boss_names]
        matches = {d.get('boss_name'): d for d in cached_data}
        missing = list(set(boss_names) - set(matches.keys())) or []
        return {'matches': matches, 'missing': missing}
