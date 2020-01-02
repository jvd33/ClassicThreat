import redis
import datetime
import json


class RedisClient:

    def __init__(self, *args, **kwargs):
        self.__redis = redis.Redis(host='localhost', port=6379, db=0)

    def get_report_results(self, report_id: str, character: str):
        cached_settings = self.__redis.get(report_id)
        if not cached_settings or cached_settings.get(character) is None:
            return None
        return json.loads(cached_settings)

    def save_results(self, report_id: str, character: str, data):
        return self.__redis.set(report_id, {character: data})
