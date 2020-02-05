from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict
from urllib.parse import urlparse

from ..utils import flatten
from ..constants import WarriorThreatValues, Spell, DruidThreatValues

FORMS = [Spell.BearForm, Spell.CatForm, Spell.BerserkerStance, Spell.BattleStance, Spell.DefensiveStance]
DAMAGE = [
    Spell.HeroicStrike8, Spell.HeroicStrike9, Spell.Revenge6, Spell.Revenge5, Spell.MockingBlow, Spell.ShieldSlam, 
    Spell.Swipe, Spell.Maul, Spell.FaerieFire, Spell.FaerieFireFeral, Spell.Cleave, Spell.Execute, Spell.ShieldBash,
    Spell.Hamstring, Spell.ThunderClap,
]

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


class FuryDPSThreatResult(BaseModel):

    def __init__(self, duration, **kwargs):
        super().__init__(**kwargs)
        self.execute_percent = self.execute_dmg/self.total_dmg * 100
        self.hs_cpm = self.hs_casts / (duration / 1000.0 / 60.0)

    player_name: str
    hs_casts: int
    execute_dmg: int
    total_dmg: int
    execute_percent: float = None
    hs_cpm: float = None


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
    enemies_in_combat: int = 1
    friendlies_in_combat: int = 1
    hit_type: int = None
    amount: float = 0
    class_modifier: int = None

    def calculate_threat(self, player_class, talent_pts=5, t1=False):
        mods = {
            'warrior': self.__warr_modifiers,
            'druid': self.__druid_modifiers,
        }.get(player_class.casefold(), None)
        raw = 0
        if not mods:    
            raise KeyError('Invalid Class Specified')
        if self.guid == Spell.Execute:
            return self.amount, self.amount
            
        if self.event_type == 'cast':
            if self.guid in [Spell.BattleShout6, Spell.BattleShout7]:
                raw = mods.get(self.guid, mods.get('noop'))(self.friendlies_in_combat, self.enemies_in_combat)
            elif self.guid == Spell.SunderArmor:
                raw = mods.get(self.guid, mods.get('noop'))(t1)
            elif self.guid not in [*DAMAGE, *FORMS]:
                raw = mods.get(self.guid, mods.get('noop'))
            

        elif self.event_type == 'damage':
            if self.guid in DAMAGE and self.hit_type not in [7, 8]:
                raw = mods.get(self.guid, mods.get('noop')) + self.amount
            elif self.guid == Spell.SunderArmor and self.hit_type in [7, 8]:
                raw = mods.get(self.guid, mods.get('noop'))(t1) * -1
            else:
                raw = self.amount

        elif self.event_type == 'heal':
            raw = mods.get('heal')(self.amount, self.enemies_in_combat)

        elif self.event_type in ['applydebuff', 'refreshdebuff'] and self.guid not in [Spell.SunderArmor, *FORMS]:
            print(self)
            raw = mods.get(self.guid, mods.get('noop'))

        elif self.event_type == 'energize':
            raw = mods.get(Spell.RageGain)(self.amount)

        if self.event_type != 'energize':
            return mods.get(self.class_modifier)(raw, talent_pts), raw

        return raw, raw



    @property
    def __warr_modifiers(self):
        __t = WarriorThreatValues.vals()
        return {
            Spell.SunderArmor: lambda x, __t=__t: __t.SunderArmor if not x else __t.SunderArmor * __t.Tier1Bonus,
            Spell.ShieldSlam: __t.ShieldSlam,
            Spell.Revenge5: __t.Revenge5,
            Spell.Revenge6: __t.Revenge6,
            Spell.HeroicStrike8: __t.HeroicStrike8,
            Spell.HeroicStrike9: __t.HeroicStrike9,
            Spell.GiftOfArthas: __t.GiftOfArthas,
            Spell.RageGain: lambda x, __t=__t: x * __t.RageGain,
            Spell.DemoShout: __t.DemoShout,
            Spell.ThunderClap: __t.ThunderClap,
            Spell.BattleShout6: lambda n, c, __t=__t: (__t.BattleShout6)/(n/c),  # N = friendlies, c = enemies
            Spell.BattleShout7: lambda n, c, __t=__t: (__t.BattleShout6)/(n/c),  # N = friendlies, c = enemies
            Spell.Cleave: __t.Cleave,
            Spell.DefensiveStance: lambda x, d, __t=__t: x * __t.DefensiveStance * getattr(__t, f'Defiance{d}'),
            Spell.BattleStance: lambda x, d, __t=__t: x * __t.BattleStance,
            Spell.BerserkerStance: lambda x, d, __t=__t: x * __t.BerserkerStance,
            Spell.Hamstring: __t.Hamstring,
            Spell.Disarm: __t.Disarm,
            Spell.ShieldBash: __t.ShieldBash,
            Spell.MockingBlow: __t.MockingBlow,
            'heal': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            'noop': 0
        }

    @property
    def __druid_modifiers(self):
        __t = DruidThreatValues.vals()
        return {
            Spell.GiftOfArthas: lambda x, __t=__t: x * __t.GiftOfArthas,
            Spell.RageGain: lambda x, __t=__t: x * __t.RageGain,
            'heal': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            Spell.DemoRoar: lambda x, n, __t=__t: x * __t.DemoRoar * n,
            Spell.BearForm: lambda x, d, __t=__t: x * (__t.BearForm + getattr(__t, f'FeralInstinct{d}')),
            Spell.CatForm: lambda x, d, __t=__t: x * __t.CatForm,
            Spell.Swipe: lambda x, __t=__t: x * __t.Swipe,
            Spell.Maul: lambda x, __t=__t: x * __t.Maul,
            Spell.FaerieFire: lambda x, __t=__t: x * __t.FaerieFire,
            Spell.FaerieFireFeral: lambda x, __t=__t: x * __t.FaerieFire,
            Spell.Cower: lambda x, __t=__t: x * __t.Cower,
            'noop': lambda x, n=None, d=None, __t=__t: 0
        }


class FightLog(BaseModel):
    boss_name: str
    boss_id: int
    report_id: str
    player_name: str
    player_class: str
    total_time: int
    dps_threat: List = list()
    events: List = list()
    realm: str
    defiance_points: int = None
    feral_instinct_points: int = None
    friendlies_in_combat: int = 1
    gear: List = None

    @staticmethod
    def from_response(resp, 
                      report_id, 
                      player_name, 
                      boss_name, 
                      boss_id,
                      total_time, 
                      player_class, 
                      modifier_events, 
                      dps_threat, 
                      gear,
                      realm, 
                      t1=False,
                      talent_pts=5,
                      friendlies=1):
        f = FightLog(
            boss_name=boss_name,
            player_name=player_name,
            boss_id=boss_id,
            report_id=report_id,
            total_time=total_time,
            player_class=player_class,
            realm=realm,
            gear=gear,
            defiance_points=talent_pts,
            feral_instinct_points=talent_pts,
            friendlies_in_combat=friendlies,
            dps_threat=[FuryDPSThreatResult(total_time, **d) for d in dps_threat if d.get('player_name') != player_name]
        )
        if player_class == 'Druid':
            f.defiance_points = None
        elif player_class == 'Warrior':
            f.feral_instinct_points = None

        modifier_event = [i for i in modifier_events if i.get('boss_name') == boss_name]
        for event in resp:
            if event.get('type') == 'damage' and event.get('targetIsFriendly', False):
                continue
            e = ThreatEvent(
                name=event.get('ability', {}).get('name', ''),
                guid=event.get('ability', {}).get('guid', 0),
                event_type=event.get('type'),
                timestamp=event.get('timestamp'),
                hit_type=event.get('hitType', None),
                amount=event.get('amount') or (event.get('resourceChange', 0) - event.get('waste', 0)) or 0,
                class_modifier=FightLog._get_event_modifier(modifier_event, event, player_class),
                enemies_in_combat=1
            )
            f.events.append(e)
        return f

    def to_resp(self):
        ret = self.dict()
        del ret['events']
        ret['events'] = [e.dict() for e in self.events]
        return ret

    @staticmethod
    def _get_event_modifier(modifier_events, event, player_class):
        default = {
            'warrior': Spell.DefensiveStance,
            'druid': Spell.BearForm
        }.get(player_class.casefold())
        if not default:
            raise KeyError('Invalid Player Class')

        time = event.get('timestamp')
        for k, rnges in [el for el in modifier_events[0].items() if el[0] != 'boss_name']:
            for rnge in rnges:
                if rnge[0] <= time and (time <= rnge[1] if rnge[1] else True):
                    return k
        return default
