from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import WarriorThreatValues, Spell
from .common import FightLog, ThreatEvent, FuryDPSThreatResult


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
    dps_threat: List = list()
    gear: List = list()


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
            Spell.DemoShout: 'demo_casts',
            Spell.BattleShout6: 'bs_casts',
            Spell.BattleShout7: 'bs_casts'
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
            if event.guid == Spell.Execute:
                self.execute_dmg += event.amount
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
                if event.hit_type not in [7, 8]:
                    setattr(self, hit_metric, getattr(self, hit_metric, 0) + 1)
                else:
                    if event.guid == Spell.SunderArmor:
                        setattr(self, 'sunder_hits', getattr(self, 'sunder_hits', 0) - 1)

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
            gear=log.gear,
            dps_threat=log.dps_threat
            
        )
        total_threat, total_threat_defiance, unmodified_tps, tps = [0, 0, 0, 0]
        for event in log.events:
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
            'refreshdebuff': self._process_debuff
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
    dps_threat: List[FuryDPSThreatResult] = list()
    gear: List[dict] = list()
