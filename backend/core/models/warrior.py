from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import WarriorThreatValues, Spell
from .common import FightLog, ThreatEvent


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
    disarm_hits: int = 0
    hamstring_hits: int = 0
    shieldbash_hits: int = 0
    mockingblow_hits: int = 0
    realm: str = None
    dps_threat: list = list()

    @property
    def __modifiers(self):
        __t = WarriorThreatValues.vals()
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
            if cached and stance == Spell.DefensiveStance:
                unmodified_threat = req.total_damage - no_d_stance.total_damage
                req.sunder_hits -= no_d_stance.sunder_hits
                req.execute_dmg = 0

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
            return modified_threat + req.execute_dmg, unmodified_threat + req.execute_dmg

        
        rage_threat = self.__modifiers.get('rage_gains')(self.rage_gains + no_d_stance.rage_gains)
        healing_threat = self.__modifiers.get('hp_gains')(self.hp_gains + no_d_stance.hp_gains, self.enemies_in_combat)
        calc_self = __calculate(self, Spell.DefensiveStance)
        calc_no_d = __calculate(no_d_stance, Spell.BattleStance) 
        unmodified_threat = sum([calc_self[1], calc_no_d[1]]) + rage_threat + healing_threat
        modified_threat = sum([calc_self[0], calc_no_d[0]]) + rage_threat + healing_threat


        unmodified_tps = unmodified_threat/(self.time or 1)
        tps = modified_threat/(self.time or 1)
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

    def process_events(self, events: List[ThreatEvent]):
        mapper = defaultdict(int)
        metrics = {
            Spell.SunderArmor: 'sunder_casts',
            Spell.HeroicStrike8: 'hs_casts',
            Spell.HeroicStrike9: 'hs_casts',
            Spell.Revenge5: 'revenge_casts',
            Spell.Revenge6: 'revenge_casts',
            Spell.Cleave: 'cleave_casts',
            Spell.Bloodthirst: 'bt_casts',
            Spell.ShieldSlam: 'shield_slam_casts',
            Spell.GiftOfArthas: 'goa_procs',
        }

        hits = {
            Spell.SunderArmor: 'sunder_hits',
            Spell.HeroicStrike8: 'hs_hits',
            Spell.HeroicStrike9: 'hs_hits',
            Spell.Revenge5: 'revenge_hits',
            Spell.Revenge6: 'revenge_hits',
            Spell.Cleave: 'cleave_hits',
            Spell.Disarm: 'disarm_hits',
            Spell.ShieldSlam: 'shield_slam_hits',
            Spell.ShieldBash: 'shieldbash_hits',
            Spell.MockingBlow: 'mockingblow_hits',
            Spell.GiftOfArthas: 'goa_procs',
            Spell.Hamstring: 'hamstring_hits',
            Spell.ThunderClap: 'thunderclap_hits',
        }

        for event in events:
            if event.event_type == 'cast':
                cast_metric = metrics.get(event.guid)
                if not cast_metric:
                    continue
                setattr(self, cast_metric, getattr(self, cast_metric, 0) + 1)
                if event.guid == Spell.SunderArmor:
                    self.sunder_hits += 1

            if event.event_type == 'damage':
                hit_metric = hits.get(event.guid)
                if not hit_metric:
                    continue
                if event.hit_type in [7, 8]:
                    setattr(self, hit_metric, getattr(self, hit_metric, 0) - 1)
                else:
                    setattr(self, hit_metric, getattr(self, hit_metric, 0) + 1)

            if event.guid == Spell.GiftOfArthas:
                self.goa_procs += 1

        return mapper

    @staticmethod
    def from_event_log(log: FightLog):
        resp = WarriorThreatCalculationRequest(
            boss_name=log.boss_name,
            boss_id=log.boss_id,
            player_class=log.player_class,
            player_name=log.player_name,
            time=log.total_time / 1000.00,
            realm=log.realm,
            defiance_points=log.defiance_points,
            friendlies_in_combat=log.friendlies_in_combat,
            
        )
        total_threat, total_threat_defiance, unmodified_tps, tps = [0, 0, 0, 0]

        for event in log.events:
            if event.event_type not in ['removedebuff']:
                modified, raw = resp._process_event(event)
                total_threat_defiance += modified
                total_threat += raw

        unmodified_tps = total_threat / resp.time
        tps = total_threat_defiance / resp.time
        event_data = resp.process_events(log.events)
        return WarriorThreatResult(
            **dict(resp),
            **event_data,
            total_threat=total_threat,
            total_threat_defiance=total_threat_defiance,
            unmodified_tps=unmodified_tps,
            tps=tps,
        )

        
    def _process_event(self, event: ThreatEvent):
        def __dummy(event: ThreatEvent):
            return 0, 0

        return {
            'damage': self._process_damage,
            'cast': self._process_cast,
            'energize': self._process_rage,
            'heal': self._process_healing,
            'applydebuff': self._process_debuff,
        }.get(event.event_type, __dummy)(event)

    def _process_damage(self, event: ThreatEvent):
        self.total_damage += event.amount
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)

    def _process_cast(self, event: ThreatEvent):
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)

    def _process_rage(self, event: ThreatEvent):
        self.rage_gains += event.amount
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)

    def _process_healing(self, event: ThreatEvent):
        self.hp_gains += event.amount
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)

    def _process_debuff(self, event: ThreatEvent):
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)


class WarriorThreatResult(WarriorThreatCalculationRequest):
    total_threat: float = 0
    total_threat_defiance: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0
