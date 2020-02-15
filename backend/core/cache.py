import asyncio
import aioredis
import datetime
import ujson
import os

from scipy.stats import percentileofscore

from .models.common import FuryDPSThreatResult, ThreatEvent

class RedisClient:

    def __init__(self, *args, **kwargs):
        self.redis_host = os.getenv('CACHE_HOST') or '0.0.0.0'

    async def save_warr_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        d = []
        for k, v in data.items():
            key = f'{report_id}:{character}:{k}'
            resp = dict(v)
            resp['t1_set'] = str(v.get('t1_set'))
            resp['dps_threat'] = ujson.dumps(v.get('dps_threat'))
            resp['events'] = ujson.dumps(v.get('events'))
            resp['gear'] = ujson.dumps(v.get('gear'))
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d


    async def save_druid_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=1))
        d = []
        for k, v in data.items():
            key = f'{report_id}:{character}:{k}'
            resp = dict(v)
            resp['dps_threat'] = ujson.dumps(v.get('dps_threat'))
            resp['gear'] = ujson.dumps(v.get('gear'))
            resp['events'] = ujson.dumps(v.get('events'))
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d


    async def save_paladin_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=5))
        d = []
        for k, v in data.items():
            key = f'{report_id}:{character}:{k}'
            resp = dict(v)
            resp['dps_threat'] = ujson.dumps(v.get('dps_threat'))
            resp['gear'] = ujson.dumps(v.get('gear'))
            resp['events'] = ujson.dumps(v.get('events'))
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d

    async def check_cache(self, report_id: str, character: str, boss_names, db=0):
        # DB 0 = Warrior parses
        # DB 1 = Druid parses
        # DB 5 = Paladin parses
        if not boss_names:
            matches = await self.get_events(report_id, character)
            matches = {d.get('boss_name'): d for d in matches}
            return {'matches': matches, 'missing': []}
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
                                                            
        cached_data = [dict(await __redis.hgetall(f'{report_id}:{character}:{b}', encoding='utf-8')) for b in boss_names]
        matches = {d.get('boss_name'): d for d in cached_data}
        missing = list(set(boss_names) - set(matches.keys())) or []
        __redis.close()
        return {'matches': matches, 'missing': missing}


    async def refresh_rank_data(self, db=2):
        # DB 2 = Warrior ranks
        # DB 3 = Druid ranks
        # DB 6 = Paladin ranks
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        last_updated = await __redis.get('last_updated', encoding='utf-8')
        if last_updated and (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(last_updated))).total_seconds() <= 60: 
            __redis.close()
            return 
        bosses = [
            'Lucifron', 'Magmadar', 'Gehennas', 'Garr', 'Shazzrah', 'Baron Geddon', 
            'Golemagg the Incinerator', 'Majordomo Executus', 'Sulfuron Harbinger', 'Ragnaros', 
            'Onyxia', 'Razorgore the Untamed', 'Vaelastrasz the Corrupt', 'Broodlord Lashlayer',
            'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus', 'Nefarian',
        ]
        await __redis.set('last_updated', ujson.dumps(datetime.datetime.now()))
        for b in bosses:
            data_db = {2: 0, 3: 1, 6: 5}.get(db)
            keys = await self._get_rank_keys(b, db=data_db)
            vals = await self._get_tps_values(keys, db=data_db)
            ranks = {k: v for k, v in sorted(vals.items(), key=lambda v: v[1], reverse=True)}
            raw_vals = [v for k, v in ranks.items()]
            ret = {
                'ranks': ujson.dumps(ranks),
                'raw_vals': ujson.dumps(raw_vals)
            }
            await __redis.hmset_dict(b, ret)
        __redis.close()

    async def _get_rank_keys(self, boss, player_name=None, db=0):
        key = f'*:{boss}' if not player_name else f'*:{player_name}:{boss}'
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        keys = await __redis.keys(key, encoding='utf-8')
        __redis.close()
        return keys

    async def _get_tps_values(self, keys, db=0):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        cached_data = [{k: await __redis.hgetall(k, encoding='utf-8')} for k in keys]
        resp = {k: float(v.get('modified_tps')) for d in cached_data for k,v in d.items() if float(v.get('modified_tps')) != 0.0}
        __redis.close()
        return resp


    async def get_encounter_percentile(self, boss_name, tps, db=2):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        data = await __redis.hgetall(boss_name, encoding='utf-8') or None
        if not data:
            return 0
        raw = ujson.loads(data.get('raw_vals'))
        __redis.close()
        return percentileofscore(raw, tps)  
        
    async def get_encounter_rankings(self, boss_name, db=2):
        data_db = {
            2: 0,
            3: 1,
            6: 5,
        }.get(db, 2)
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        data = await __redis.hgetall(boss_name, encoding='utf-8')
        ranks = ujson.loads(data.get('ranks') or '{}')   
        for key, threat in ranks.items():
            data = await self.get_by_key(key, data_db)
            ranks[key] = {
                'player': data.get('player_name'),
                'boss': data.get('boss_name'),
                'realm': data.get('realm'),
                'modified_threat': threat,
                'modified_tps': data.get('modified_tps') or data.get('total_tps_defiance') or data.get('total_tps_feral_instinct') or data.get('total_tps_imp_rf'),
                'report': key.split(':')[0],
                'boss_id': data.get('boss_id'),
            }
        __redis.close()
        return ranks  

    async def get_by_key(self, key, db=0):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        data = await __redis.hgetall(key, encoding='utf-8')
        __redis.close()
        return data

    async def save_events(self, report_id, player_name, all_events):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=4))
        for k, v in all_events.items():
            key = f'{report_id}:{player_name}:{k}'
            cache_result = v.dict()
            cache_result['dps_threat'] = ujson.dumps([d.dict() for d in v.dps_threat])
            cache_result['gear'] = ujson.dumps([dict(d) for d in v.gear])

            await __redis.hmset_dict(key, cache_result)
        __redis.close()

    async def get_events(self, report_id, player_name, bosses=None):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=4))
        d = []
        if not bosses:
            key = f'{report_id}:{player_name}:*'
            keys = await __redis.keys(key, encoding='utf-8')
        else:
            keys = [f'{report_id}:{player_name}:{boss}' for boss in bosses]

        for key in keys:
            r = await __redis.hgetall(key, encoding='utf-8')
            if not r:
                continue

            r['dps_threat'] = [FuryDPSThreatResult(int(r['total_time']), **f) for f in ujson.loads(r['dps_threat'])]
            r['events'] = [ThreatEvent(**e) for e in ujson.loads(r['events'])]
            r['gear'] = [i for i in ujson.loads(r['gear'])]
            d.append(r)
        __redis.close()
        
        return d
