from pydantic import BaseModel, AnyUrl, validator
from typing import List

from .constants import ThreatValues

class ClassDPS(BaseModel):
    class_name: str
    dps: float = 0.0


class WCLDataRequest(BaseModel):
    url: AnyUrl
    player_name: str
    defiance_points: int = 5
    bosses: List[str] = None
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1
    t1_set: bool = False

    @validator('url')
    def check_url(cls, v):
        assert v.host == 'classic.warcraftlogs.com' and v.path and len(v.path) > 1 and 'reports' in v.path, \
        "Invalid Log URL."
        return v

class BossActivityRequest(BaseModel):
    player_id: int
    start_time: int
    end_time: int
    encounter: int
    report_id: str
    boss_name: str


class WarriorThreatCalculationRequest(BaseModel):
    shield_slam_count: int = 0
    bt_count: int = 0
    revenge_count: int = 0
    hs_count: int = 0
    sunder_count: int = 0
    execute_dmg: int = 0
    goa_procs: int = 0
    rage_gains: int = 0
    time: float
    total_damage: int = 0
    t1_set: bool = False
    defiance_points: int = 5
    bs_casts: int = 0
    demo_casts: int = 0
    thunderclap_casts: int = 0
    hp_gains: float = 0
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1  # for healing and shout threat
    player_name: str
    player_class: str
    boss_name: str
    boss_id: int
    realm: str


    defiance_key = f'Defiance{defiance_points}'
    __t = ThreatValues.vals()
    __modifiers = {
        'sunder_count': lambda x, t1, __t=__t: x * __t.SunderArmor if not t1 else x * __t.SunderArmor * __t.Tier1Bonus,
        'shield_slam_count': lambda x, __t=__t: x * __t.ShieldSlam,
        'revenge_count': lambda x, __t=__t: x * __t.Revenge,
        'hs_count': lambda x, __t=__t: x * __t.HeroicStrike,
        'goa_procs': lambda x, __t=__t: x * __t.GiftOfArthas,
        'rage_gains': lambda x, __t=__t: x * __t.RageGain,
        'hp_gains': lambda x, n, __t=__t: x * __t.Healing / n, # Split
        'demo_casts': lambda x, n, __t=__t: x * __t.DemoShout / n,
        'thunderclap_casts': lambda x, __t=__t: x * __t.ThunderClap,
        'bs_casts': lambda x, n, c, __t=__t: (x * __t.BattleShout)/(n/c),  # N = friendlies, c = enemies
    }

    def calculate_warrior_threat(self):
        exclude = {'time', 't1_set', 'total_damage', 'execute_dmg', 'player_name', 'player_class', 'realm', 'bt_count',
                   'defiance_points', 'friendlies_in_combat', 'enemies_in_combat', 'thunderclap_casts', 'boss_name',
                   '__modifiers', 'defiance_key', '__t', 'boss_id'}

        unmodified_threat = self.total_damage
        for name, val in self.copy(exclude=exclude):
            if name == 'sunder_count':
                unmodified_threat += self.__modifiers.get(name)(val, self.t1_set)
            elif name == 'bs_casts':
                if val <= 0:
                    continue

                # TODO Haven't checked, but I could probably parse out the # of targets actually affected by this Battle Shout
                unmodified_threat += self.__modifiers.get(name)(val, self.friendlies_in_combat, self.enemies_in_combat)
            elif name in ['hp_gains', 'demo_casts']:
                unmodified_threat += self.__modifiers.get(name)(val, self.enemies_in_combat)
            else:
                unmodified_threat += self.__modifiers.get(name)(val)
        tc_threat = self.__modifiers.get('thunderclap_casts')(self.thunderclap_casts)

        modified_threat = unmodified_threat * self.__t.DefensiveStance * getattr(self.__t, self.defiance_key)

        unmodified_threat = unmodified_threat + tc_threat
        unmodified_tps = unmodified_threat/self.time
        tps = (modified_threat + tc_threat)/self.time

        return dict(WarriorThreatResult(
            **dict(self),
            total_threat=unmodified_threat,
            total_threat_defiance=modified_threat,
            unmodified_tps=unmodified_tps,
            tps=tps
        ))


class WarriorThreatResult(WarriorThreatCalculationRequest):
    total_threat: float = 0
    total_threat_defiance: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0
    dps_caps: List[ClassDPS] = None


class WarriorCastResponse(BaseModel):
    shield_slam_count: int = 0
    revenge_count: int = 0
    hs_count: int = 0
    goa_procs: int = 0
    bs_casts: int = 0
    demo_casts: int = 0
    thunderclap_casts: int = 0
    bt_count: int = 0


class WarriorDamageResponse(BaseModel):
    total_damage: int = 0
    execute_dmg: int = 0
    sunder_count: int = 0
    time: int = 0
