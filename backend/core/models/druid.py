from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import DruidThreatValues, Spell

class DruidThreatCalculationRequest(BaseModel):

    goa_procs: int = 0
    rage_gains: int = 0
    time: float = 0
    total_damage: int = 0
    feral_instinct_points: int = 5
    ff_hits: int = 0
    swipe_dmg: int = 0
    maul_dmg: int = 0
    swipe_casts: int = 0
    maul_casts: int = 0
    demo_casts: int = 0
    cower_casts: int = 0
    hp_gains: float = 0
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1  # for healing and shout threat
    player_name: str = None
    player_class: str = None
    boss_name: str = None
    boss_id: int = None

    realm: str = None
    no_bear: Dict = None

    @property
    def __modifiers(self):
        __t = DruidThreatValues.vals()
        return {
           
            'goa_procs': lambda x, __t=__t: x * __t.GiftOfArthas,
            'rage_gains': lambda x, __t=__t: x * __t.RageGain,
            'hp_gains': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            'demo_casts': lambda x, n, __t=__t: x * __t.DemoRoar * n,
            
            Spell.BearForm: lambda x, d, __t=__t: x * (__t.BearForm + getattr(__t, f'FeralInstinct{d}')),
            Spell.CatForm: lambda x, d, __t=__t: x * __t.CatForm,
            'swipe_dmg': lambda x, __t=__t: x * __t.Swipe,
            'maul_dmg': lambda x, __t=__t: x * __t.Maul,
            'ff_hits': lambda x, __t=__t: x * __t.FaerieFire,
            'cower_casts': lambda x, __t=__t: x * __t.Cower,

        }

    def calculate_druid_threat(self, cached=False):
        exclude = {
            'time', 'total_damage', 'player_name', 'player_class', 'realm', 
            'feral_instinct_points', 'friendlies_in_combat', 'enemies_in_combat', 'boss_name', 'no_bear',
            '__modifiers', '__t', 'boss_id', 'rage_gains', 'hp_gains', 'ff_casts', 'swipe_casts', 'maul_casts'
            
        }

        no_bear= DruidThreatCalculationRequest(**self.no_bear)

        def __calculate(req, stance):
            unmodified_threat = req.total_damage
            for name, val in req.copy(exclude=exclude):
                if name == 'demo_casts':
                    unmodified_threat += self.__modifiers.get(name)(val, self.enemies_in_combat)
                else:
                    unmodified_threat += self.__modifiers.get(name)(val)
            
            modified_threat = self.__modifiers.get(stance)(unmodified_threat, self.feral_instinct_points)
            return modified_threat, unmodified_threat

            
        rage_threat = self.__modifiers.get('rage_gains')(self.rage_gains)
        healing_threat = self.__modifiers.get('hp_gains')(self.hp_gains, self.enemies_in_combat)
        calc_self = __calculate(self, Spell.BearForm)
        calc_no_d = __calculate(no_bear, Spell.CatForm) 
        unmodified_threat = sum([calc_self[1], calc_no_d[1]]) + rage_threat + healing_threat
        modified_threat = sum([calc_self[0], calc_no_d[0]]) + rage_threat + healing_threat

        self.total_damage = self.total_damage + self.maul_dmg + self.swipe_dmg

        unmodified_tps = unmodified_threat/self.time
        tps = modified_threat/self.time
        if not cached:
            for name, val in dict(self).items():
                if '_casts' in name or '_hits' in name or '_dmg' in name or '_damage' in name:
                    setattr(self, name, getattr(self, name) + self.no_bear.get(name, 0))

        return dict(DruidThreatResult(
            **dict(self),
            total_threat=unmodified_threat,
            total_threat_feral_instinct=modified_threat,
            unmodified_tps=unmodified_tps,
            tps=tps,
        ))


class DruidThreatResult(DruidThreatCalculationRequest):
    total_threat: float = 0
    total_threat_feral_instinct: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0

class DruidCastResponse(BaseModel):
    goa_procs: int = 0
    demo_casts: int = 0
    cower_casts: int = 0
    swipe_casts: int = 0
    maul_casts: int = 0
    ff_hits: int = 0

class DruidDamageResponse(BaseModel):
    total_damage: int = 0
    time: int = 0
    enemies_in_combat: int = 0
    swipe_hits: int = 0
    swipe_dmg: float = 0
    maul_hits: int = 0
    maul_dmg: float = 0


class ShapeshiftEvent(BaseModel):
    rage_gains: int = 0
    hp_gains: float = 0


