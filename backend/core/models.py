from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from .constants import WarriorThreatValues, Spell

class ClassDPS(BaseModel):
    class_name: str
    dps: float = 0.0


class WCLDataRequest(BaseModel):
    url: AnyUrl
    player_name: str
    defiance_points: int = 5
    bosses: List[str] = []
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1
    t1_set: bool = False

    @validator('url')
    def check_url(cls, v):
        assert v.host == 'classic.warcraftlogs.com' and v.path and len(v.path) > 1 and 'reports' in v.path, \
        "Invalid Log URL."
        return v


    @validator('defiance_points')
    def check_defiance(cls, v):
        assert v in [0, 1, 2, 3, 4, 5], "0 through 5."
        return v


class StanceDanceEvent(BaseModel):
    rage_gains: int = 0
    hp_gains: float = 0


class BossActivityRequest(BaseModel):
    player_id: int
    start_time: int
    end_time: int
    encounter: int
    report_id: str
    boss_name: str


class WarriorThreatCalculationRequest(BaseModel):
    shield_slam_hits: int = 0
    bt_casts: int = 0
    revenge_hits: int = 0
    revenge_casts: int = 0
    shield_slam_casts: int = 0
    hs_casts: int = 0
    hs_hits: int = 0
    sunder_hits: int = 0
    sunder_casts: int = 0
    execute_dmg: int = 0
    goa_procs: int = 0
    rage_gains: int = 0
    time: float = 0
    total_damage: int = 0
    t1_set: bool = False
    defiance_points: int = 5
    cleave_hits: int = 0
    cleave_casts: int = 0
    bs_casts: int = 0
    demo_casts: int = 0
    thunderclap_hits: int = 0
    hp_gains: float = 0
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1  # for healing and shout threat
    player_name: str = None
    player_class: str = None
    boss_name: str = None
    boss_id: int = None
    hs_rank: int = None
    bs_rank: int = None
    disarm_hits: int = 0
    hamstring_hits: int = 0
    shieldbash_hits: int = 0
    mockingblow_hits: int = 0
    revenge_rank: int = None
    realm: str = None
    no_d_stance: Dict = None

    @property
    def __modifiers(self):
        __t = WarriorThreatValues.vals(self.hs_rank, self.revenge_rank, self.bs_rank)
        return {
            'sunder_hits': lambda x, t1, __t=__t: x * __t.SunderArmor if not t1 else x * __t.SunderArmor * __t.Tier1Bonus,
            'shield_slam_hits': lambda x, __t=__t: x * __t.ShieldSlam,
            'revenge_hits': lambda x, __t=__t: x * __t.Revenge,
            'hs_hits': lambda x, __t=__t: x * __t.HeroicStrike,
            'goa_procs': lambda x, __t=__t: x * __t.GiftOfArthas,
            'rage_gains': lambda x, __t=__t: x * __t.RageGain,
            'hp_gains': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            'demo_casts': lambda x, n, __t=__t: x * __t.DemoShout * n,
            'thunderclap_hits': lambda x, __t=__t: x * __t.ThunderClap,
            'bs_casts': lambda x, n, c, __t=__t: (x * __t.BattleShout)/(n/c),  # N = friendlies, c = enemies
            'cleave_hits': lambda x, __t=__t: x * __t.Cleave,
            Spell.DefensiveStance: lambda x, d, __t=__t: x * __t.DefensiveStance * getattr(__t, f'Defiance{d}'),
            Spell.BattleStance: lambda x, d, __t=__t: x * __t.BattleStance,
            Spell.BerserkerStance: lambda x, d, __t=__t: x * __t.BerserkerStance,
            'hamstring_hits': lambda x, __t=__t: x * __t.Hamstring,
            'disarm_hits': lambda x, __t=__t: x * __t.Disarm,
            'shieldbash_hits': lambda x, __t=__t: x * __t.ShieldBash,
            'mockingblow_hits': lambda x, __t=__t: x * __t.MockingBlow,

        }

    def calculate_warrior_threat(self, cached=False):
        exclude = {
            'time', 't1_set', 'total_damage', 'execute_dmg', 'player_name', 'player_class', 'realm', 'bt_casts',
            'defiance_points', 'friendlies_in_combat', 'enemies_in_combat', 'boss_name', 'no_d_stance',
            '__modifiers', 'defiance_key', '__t', 'boss_id', 'rage_gains', 'hp_gains', 'shield_slam_casts', 
            'revenge_casts', 'hs_casts', 'sunder_casts', 'bs_rank', 'hs_rank', 'revenge_rank', 'cleave_casts',
        }

        no_d_stance = WarriorThreatCalculationRequest(**self.no_d_stance)

        def __calculate(req, stance):
            unmodified_threat = req.total_damage
            for name, val in req.copy(exclude=exclude):
                if name == 'sunder_hits':
                    unmodified_threat += self.__modifiers.get(name)(val, self.t1_set)
                elif name == 'bs_casts':
                    # TODO Haven't checked, but I could probably parse out the # of targets actually affected by this Battle Shout
                    unmodified_threat += self.__modifiers.get(name)(val, self.friendlies_in_combat, self.enemies_in_combat)
                elif name == 'demo_casts':
                    unmodified_threat += self.__modifiers.get(name)(val, self.enemies_in_combat)
                else:
                    unmodified_threat += self.__modifiers.get(name)(val)
            
            modified_threat = self.__modifiers.get(stance)(unmodified_threat, self.defiance_points)
            unmodified_threat = unmodified_threat + req.execute_dmg
            return modified_threat, unmodified_threat

        
        rage_threat = self.__modifiers.get('rage_gains')(self.rage_gains)
        healing_threat = self.__modifiers.get('hp_gains')(self.hp_gains, self.enemies_in_combat)
        calc_self = __calculate(self, Spell.DefensiveStance)
        calc_no_d = __calculate(no_d_stance, Spell.BattleStance) 
        unmodified_threat = sum([calc_self[1], calc_no_d[1]])
        modified_threat = sum([calc_self[0], calc_no_d[0]])

        unmodified_tps = (unmodified_threat + rage_threat + healing_threat)/self.time
        tps = (modified_threat + rage_threat + healing_threat)/self.time
        if not cached:
            for name, val in dict(self).items():
                if '_casts' in name or '_hits' in name or '_dmg' in name or '_damage' in name:
                    setattr(self, name, getattr(self, name) + self.no_d_stance.get(name, 0))

        return dict(WarriorThreatResult(
            **dict(self),
            total_threat=unmodified_threat,
            total_threat_defiance=modified_threat,
            unmodified_tps=unmodified_tps,
            tps=tps,
        ))

class WarriorThreatResult(WarriorThreatCalculationRequest):
    total_threat: float = 0
    total_threat_defiance: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0


class WarriorCastResponse(BaseModel):
    shield_slam_casts: int = 0
    revenge_casts: int = 0
    hs_casts: int = 0
    goa_procs: int = 0
    bs_casts: int = 0
    demo_casts: int = 0
    thunderclap_casts: int = 0
    bt_casts: int = 0
    cleave_casts: int = 0
    bs_rank: int = Spell.BattleShout6
    revenge_rank: int = Spell.Revenge5
    hs_rank: int = Spell.HeroicStrike8
    sunder_casts: int = 0


class WarriorDamageResponse(BaseModel):
    total_damage: int = 0
    execute_dmg: int = 0
    sunder_misses: int = 0
    sunder_casts: int = 0
    shield_slam_hits: int = 0
    revenge_hits: int = 0
    hs_hits: int = 0
    time: int = 0
    mockingblow_hits: int = 0
    hamstring_hits: int = 0
    thunderclap_hits: int = 0
    disarm_hits: int = 0
    shieldbash_hits: int = 0
    enemies_in_combat: int = 0
    cleave_hits: int = 0
