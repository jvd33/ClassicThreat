import asyncio
import aioredis
import datetime
import ujson
import os

from scipy.stats import percentileofscore

class RedisClient:

    def __init__(self, *args, **kwargs):
        self.redis_host = os.getenv('CACHE_HOST') or '0.0.0.0'

    async def get_report_results(self, report_id: str, character: str):
        key = f'{report_id}:{character}*'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        keys = await __redis.keys(key, encoding='utf-8')                                  
        cached_data = [dict(await __redis.hgetall(key, encoding='utf-8')) for key in keys]
        resp = {d.get('boss_name'): d for d in cached_data}
        __redis.close()
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
        __redis.close()
        return {'matches': matches, 'missing': missing}


    async def refresh_rank_data(self):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=2))
        last_updated = await __redis.get('last_updated', encoding='utf-8')
        if last_updated and (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(last_updated))).total_seconds() <= (3600 * 6): 
            __redis.close()
            return 
        bosses = [
            'Lucifron', 'Magmadar', 'Gehennas', 'Garr', 'Shazzrah', 'Baron Geddon', 
            'Golemagg the Incinerator', 'Majordomo Executus', 'Sulfuron Harbinger', 'Ragnaros', 
            'Onyxia',
        ]
        await __redis.set('last_updated', ujson.dumps(datetime.datetime.now()))
        for b in bosses:
            keys = await self._get_rank_keys(b)
            vals = await self._get_tps_values(keys)
            ranks = {k: v for k, v in sorted(vals.items(), key=lambda v: v[1], reverse=True)}
            raw_vals = [v for k, v in ranks.items()]
            ret = {
                'ranks': ujson.dumps(ranks),
                'raw_vals': ujson.dumps(raw_vals)
            }
            await __redis.hmset_dict(b, ret)
        __redis.close()

    async def _get_rank_keys(self, boss, player_name=None):
        key = f'*:{boss}' if not player_name else f'*:{player_name}:{boss}'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        keys = await __redis.keys(key, encoding='utf-8')
        __redis.close()
        return keys

    async def _get_tps_values(self, keys):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        cached_data = [{k: await __redis.hgetall(k, encoding='utf-8')} for k in keys]
        resp = {k: float(v.get('tps')) for d in cached_data for k,v in d.items() if float(v.get('tps')) != 0.0}
        __redis.close()
        return resp


    async def get_encounter_percentile(self, boss_name, tps):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=2))
        data = await __redis.hgetall(boss_name, encoding='utf-8') or None
        if not data:
            return 0
        raw = ujson.loads(data.get('raw_vals'))
        __redis.close()
        return percentileofscore(raw, tps)  
        
    async def get_encounter_rankings(self, boss_name):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=2))
        data = await __redis.hgetall(boss_name, encoding='utf-8')
        ranks = ujson.loads(data.get('ranks'))   
        __redis.close()
        return ranks  