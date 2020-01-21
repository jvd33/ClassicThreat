from pydantic import BaseModel, AnyUrl, validator
from typing import List


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