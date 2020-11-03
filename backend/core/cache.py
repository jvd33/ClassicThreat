import asyncio
import aioredis
import datetime
import ujson
import os
import lz4.frame

from scipy.stats import percentileofscore

from .models.common import FuryDPSThreatResult, ThreatEvent

class RedisClient:

    def __init__(self, *args, **kwargs):
        self.redis_host = os.getenv('CACHE_HOST') or '0.0.0.0'

    async def save_warr_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=0))
        d = []
        for v in data.values():
            if not v.get('is_kill', False):
                continue

            boss_name = v.get('boss_name')
            key = f'{report_id}:{character}:{boss_name}'
            resp = dict(v)
            resp['t1_set'] = str(v.get('t1_set'))
            resp['dps_threat'] = lz4.frame.compress(ujson.dumps(v.get('dps_threat')).encode())
            resp['events'] = lz4.frame.compress(ujson.dumps(v.get('events')).encode())
            resp['gear'] = lz4.frame.compress(ujson.dumps(v.get('gear')).encode())
            resp['is_kill'] = ujson.dumps(v.get('is_kill'))
            resp['inserted_at'] = ujson.dumps(datetime.datetime.now())
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d


    async def save_druid_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=1))
        d = []
        for v in data.values():
            if not v.get('is_kill', False):
                continue

            boss_name = v.get('boss_name')
            key = f'{report_id}:{character}:{boss_name}'
            resp = dict(v)
            resp['is_kill'] = ujson.dumps(v.get('is_kill'))
            resp['dps_threat'] = lz4.frame.compress(ujson.dumps(v.get('dps_threat')).encode())
            resp['events'] = lz4.frame.compress(ujson.dumps(v.get('events')).encode())
            resp['gear'] = lz4.frame.compress(ujson.dumps(v.get('gear')).encode())
            resp['inserted_at'] = ujson.dumps(datetime.datetime.now())
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d


    async def save_paladin_results(self, report_id: str, character: str, data):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=5))
        d = []
        for v in data.values():
            if not v.get('is_kill', False):
                continue

            boss_name = v.get('boss_name')
            key = f'{report_id}:{character}:{boss_name}'
            resp = dict(v)
            resp['dps_threat'] = lz4.frame.compress(ujson.dumps(v.get('dps_threat')).encode())
            resp['events'] = lz4.frame.compress(ujson.dumps(v.get('events')).encode())
            resp['gear'] = lz4.frame.compress(ujson.dumps(v.get('gear')).encode())
            resp['is_kill'] = ujson.dumps(v.get('is_kill'))
            resp['inserted_at'] = ujson.dumps(datetime.datetime.now())
            await __redis.delete(key)
            r = await __redis.hmset_dict(key, resp)
            d.append(r)
        __redis.close()
        return d

    async def check_cache(self, report_id: str, character: str, boss_names, include_wipes, db=0):
        # DB 0 = Warrior parses
        # DB 1 = Druid parses
        # DB 5 = Paladin parses
        matches = await self.get_events(report_id, character)
        matches = {d.get('boss_id'): d for d in matches}
        if boss_names:
            matches = {d.get('boss_id'): d for d in matches.values() if d.get('boss_name') in boss_names}
        if not include_wipes:
            matches = {d.get('boss_id'): d for d in matches.values() if d.get('is_kill')}
        names = [match.get('boss_name') for match in matches.values()]
        missing = list(set(boss_names) - set(names)) or []
        return {'matches': matches, 'missing': missing}


    async def refresh_rank_data(self, db=2):
        # DB 2 = Warrior ranks
        # DB 3 = Druid ranks
        # DB 6 = Paladin ranks
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        last_updated = await __redis.get('last_updated', encoding='utf-8')
        if last_updated and (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(last_updated))).total_seconds() <= 300: 
            __redis.close()
            return 
        bosses = [
            'The Prophet Skeram', 'Silithid Royalty', 'Battleguard Sartura', 'Fankriss the Unyielding', 
            'Princess Huhuran', 'Twin Emperors', 'Ouro', 'C\'Thun',

            'Kurinnaxx', 'General Rajaxx', 'Moam', 'Buru the Gorger', 'Ayamiss the Hunter', 'Ossirian the Unscarred',

            'High Priest Venoxis', 'High Priestess Jeklik', 'High Priestess Mar\'li', 
            'Bloodlord Mandokir', 'Edge of Madness', 'High Priest Thekal', ' Gahz\'ranka', 
            'High Priestess Arlokk', 'Jin\'do the Hexxer', 'Hakkar',

            'Razorgore the Untamed', 'Vaelastrasz the Corrupt', 'Broodlord Lashlayer', 
            'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus', 'Nefarian', 

            'Lucifron', 'Magmadar', 'Gehennas', 'Garr', 'Shazzrah', 
            'Baron Geddon', 'Golemagg the Incinerator', 'Majordomo Executus', 
            'Sulfuron Harbinger', 'Ragnaros', 

            'Onyxia',
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
        cached_data = {k: await __redis.hget(k, 'modified_tps', encoding='utf-8') for k in keys}
        __redis.close()
        return cached_data


    async def get_encounter_percentile(self, boss_name, tps, db=2):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        data = await __redis.hgetall(boss_name, encoding='utf-8') or None
        if not data:
            return 0
        raw = ujson.loads(data.get('raw_vals'))
        __redis.close()
        raw = [float(x) for x in raw]
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
                'tps': float(threat),
                'total_threat': float(data.get('modified_threat')),
                'report': key.split(':')[0],
                'boss_id': int(data.get('boss_id')),
            }
                    
        dedupe = []
        ranks = {k: v for k, v in sorted(ranks.items(), key=lambda r: r[1].get('tps', 0), reverse=True)}
        final = {}
        for key, rank in ranks.items():
            player, realm, boss = rank.get('player'), rank.get('realm'), rank.get('boss')
            player_key = f'{player}:{realm}:{boss}'
            if player_key not in dedupe:
                dedupe.append(player_key)
                final[key] = rank
        __redis.close()
        return final

    async def get_by_key(self, key, db=0):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=db))
        fields = ['player_name', 'boss_name', 'realm', 'modified_threat', 'boss_id']
        data = await __redis.hmget(key, *fields, encoding='utf-8')
        data = {field: value for field, value in zip(fields, data)}
        __redis.close()
        return data

    async def save_events(self, report_id, player_name, log):
        __redis = await aioredis.Redis(await aioredis.create_connection((self.redis_host, 6379), db=4))
        key = f'{report_id}:{player_name}:{log.boss_id}'
        cache_result = log.dict()
        cache_result['dps_threat'] = lz4.frame.compress(ujson.dumps([d.dict() for d in log.dps_threat]).encode())
        cache_result['events'] = lz4.frame.compress(ujson.dumps([d.dict() for d in log.events]).encode())
        cache_result['gear'] = lz4.frame.compress(ujson.dumps([dict(d) for d in log.gear]).encode())
        cache_result['is_kill'] = ujson.dumps(log.is_kill)
        cache_result['aggro_windows'] = lz4.frame.compress(ujson.dumps(log.aggro_windows).encode())
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
            r = await __redis.hgetall(key)
            if not r:
                continue
            r = {k.decode('utf-8'): v for k, v in r.items()}
            r['dps_threat'] = [FuryDPSThreatResult(int(r['total_time']), **f) for f in ujson.loads(lz4.frame.decompress(r['dps_threat']))]
            r['events'] = [ThreatEvent(**e) for e in ujson.loads(lz4.frame.decompress(r['events']))]
            r['gear'] = [i for i in ujson.loads(lz4.frame.decompress(r['gear']))]
            r['is_kill'] = ujson.loads(r.get('is_kill', True))
            r['aggro_windows'] = ujson.loads(lz4.frame.decompress(r['aggro_windows']))
            r = {k: v.decode() if isinstance(v, bytes) else v for k, v in r.items()}
            d.append(r)
        __redis.close()
        
        return d
