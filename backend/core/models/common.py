from pydantic import BaseModel, AnyUrl, validator
from typing import List
from urllib.parse import urlparse
from ..utils import flatten

class WCLDataRequest(BaseModel):
    url: AnyUrl
    player_name: str
    defiance_points: int = None
    feral_instinct_points: int = None
    bosses: List[str] = []
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1
    t1_set: bool = False

    @validator('url')
    def check_url(cls, v):
        assert v.host == 'classic.warcraftlogs.com' and v.path and len(v.path) > 1 and 'reports' in v.path, \
        "Invalid Log URL."
        return v


    @validator('defiance_points', allow_reuse=True)
    @validator('feral_instinct_points', allow_reuse=True)
    def check_5pt_talent(cls, v):
        assert v in [0, 1, 2, 3, 4, 5], "0 through 5."
        return v

    @property
    def report_id(self):
        url_segments = urlparse(self.url)
        seg = url_segments.path.split('/')
        report_index = next((i for i, s  in enumerate(seg) if s == 'reports'), None)
        if not report_index or len(url_segments) <= report_index:
            return None
        report_id = seg[report_index + 1]
        return report_id

class ClassDPS(BaseModel):
    class_name: str
    dps: float = 0.0


class BossActivityRequest(BaseModel):
    player_id: int
    start_time: int
    end_time: int
    encounter: int
    report_id: str
    boss_name: str


class Rank(BaseModel):
    name: str
    encounter: str
    report_id: str
    tps: str

class ThreatEvent(BaseModel):
    name: str
    guid: int
    event_type: str
    timestamp: int

    hit_type: int = None
    amount: float = None


class FightLog(BaseModel):
    boss_name: str
    report_id: str
    player_name: str
    
    events: List = list()

    @staticmethod
    def from_response(resp, report_id, player_name, boss_name):
        f = FightLog(
            boss_name=boss_name,
            player_name=player_name,
            report_id=report_id
        )
        for event in resp:
            e = ThreatEvent(
                name=event.get('ability', {}).get('name', ''),
                guid=event.get('ability', {}).get('guid', 0),
                event_type=event.get('type'),
                timestamp=event.get('timestamp'),
                hit_type=event.get('hitType', None),
                amount=event.get('amount') or event.get('resourceChange') or 0
            )
            f.events.append(e)
        return f

    def to_resp(self):
        ret = self.dict()
        del ret['events']
        ret['events'] = [e.dict() for e in self.events]
        return ret