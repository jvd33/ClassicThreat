from pydantic import BaseModel
from typing import List


class ClassDPS(BaseModel):
    class_name: str
    dps: float = 0.0


class WCLDataRequest(BaseModel):
    url: str
    player_name: str
    bosses: List[str] = None


class BossActivityRequest(BaseModel):
    player_id: int
    start_time: int
    end_time: int
    encounter: int
    report_id: str


class WarriorThreatCalculationRequest(BaseModel):
    shield_slam_count: int = 0
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
    realm: str

    __modifiers = {
        'd_stance': 1.3,
        'sunder_count': lambda x, t1: x * 261 if not t1 else x * 261 * 1.15,
        'shield_slam_count': lambda x: x * 250,
        'revenge_count': lambda x: x * 315,
        'hs_count': lambda x: x * 145,
        'goa_procs': lambda x: x * 90,
        'rage_gains': lambda x: x * 5,
        'defiance': {
            0: 1,
            1: 1.03,
            2: 1.06,
            3: 1.09,
            4: 1.12,
            5: 1.15
        },
        'hp_gains': lambda x: x * .5,
        'demo_casts': lambda x: x * 42,
        'thunderclap_casts': lambda x: x * 314 * .8,
        'bs_casts': lambda x, n, c: (x * 56)/(n/c),
    }

    def calculate_warrior_threat(self):
        exclude = {'time', 't1_set', 'total_damage', 'execute_dmg', 'player_name', 'player_class', 'realm',
                   'defiance_points', 'friendlies_in_combat', 'enemies_in_combat', 'thunderclap_casts'}
        unmodified_threat = self.total_damage
        for name, val in self.copy(exclude=exclude):
            if name == 'sunder_count':
                unmodified_threat += self.__modifiers.get(name)(val, self.t1_set)
            elif name == 'bs_casts':
                if val <= 0:
                    continue
                unmodified_threat += self.__modifiers.get(name)(val, self.friendlies_in_combat, self.enemies_in_combat)
            else:
                unmodified_threat += self.__modifiers.get(name)(val)
        tc_threat = self.__modifiers.get('thunderclap_casts')(self.thunderclap_casts)

        unmodified_threat = unmodified_threat + tc_threat
        modified_threat = (unmodified_threat - self.execute_dmg) \
            * self.__modifiers.get('d_stance') * self.__modifiers.get('defiance').get(self.defiance_points)

        unmodified_tps = unmodified_threat/self.time
        tps = (modified_threat + self.execute_dmg)/self.time
        return WarriorThreatResult(
            **dict(self),
            total_threat=unmodified_threat,
            total_threat_defiance=modified_threat,
            unmodified_tps=unmodified_tps,
            tps=tps
        )


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


class WarriorDamageResponse(BaseModel):
    total_damage: int = 0
    execute_dmg: int = 0
    sunder_count: int = 0
    time: int = 0
