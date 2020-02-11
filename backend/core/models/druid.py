from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import DruidThreatValues, Spell
from .common import ThreatEvent, FightLog

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
    dps_threat: List = list()
    gear: List = list()


    def process_events(self, events: List[ThreatEvent]):
        mapper = defaultdict(int)
        metrics = {
            Spell.Maul: 'maul_casts',
            Spell.Swipe: 'swipe_casts',
            Spell.DemoRoar: 'demo_casts',
            Spell.GiftOfArthas: 'goa_procs',
            Spell.Cower: 'cower_casts',
        }

        hits = {
            Spell.Maul: 'maul_dmg',
            Spell.Swipe: 'swipe_dmg',
            Spell.FaerieFireFeral: 'ff_hits',
            Spell.FaerieFire: 'ff_hits',
            Spell.DemoRoar: 'demo_casts',
            Spell.GiftOfArthas: 'goa_procs',
        }

        for event in events:
            if event.event_type == 'cast':
                cast_metric = metrics.get(event.guid)
                if not cast_metric:
                    continue
                setattr(self, cast_metric, getattr(self, cast_metric, 0) + 1)

            if event.event_type == 'damage':
                hit_metric = hits.get(event.guid)
                if not hit_metric:
                    continue
                if event.hit_type not in [7, 8]:
                    if event.guid in [Spell.Swipe, Spell.Maul]:
                        setattr(self, hit_metric, getattr(self, hit_metric, 0) + event.amount)
                        continue
                    setattr(self, hit_metric, getattr(self, hit_metric, 0) + 1)
                    

            if event.guid == Spell.GiftOfArthas:
                self.goa_procs += 1

        return mapper

    @staticmethod
    def from_event_log(log: FightLog):
        resp = DruidThreatCalculationRequest(
            boss_name=log.boss_name,
            boss_id=log.boss_id,
            player_class=log.player_class,
            player_name=log.player_name,
            time=log.total_time / 1000.00,
            realm=log.realm,
            feral_instinct_points=log.feral_instinct_points,
            friendlies_in_combat=log.friendlies_in_combat,
            gear=log.gear,
            dps_threat=log.dps_threat
        )
        total_threat, total_threat_feral_instinct, unmodified_tps, tps = [0, 0, 0, 0]
        for event in log.events:
            modified, raw = resp._process_event(event)
            total_threat_feral_instinct += modified
            total_threat += raw

        unmodified_tps = total_threat / resp.time
        tps = total_threat_feral_instinct / resp.time
        event_data = resp.process_events(log.events)
        return DruidThreatResult(
            **dict(resp),
            **event_data,
            total_threat=total_threat,
            total_threat_feral_instinct=total_threat_feral_instinct,
            unmodified_tps=unmodified_tps,
            tps=tps,
        )

        
    def _process_event(self, event: ThreatEvent):
        def __dummy(event: ThreatEvent):
            return 0, 0

        return {
            'damage': self._process_damage,
            'cast': self.__process_event,
            'energize': self._process_rage,
            'heal': self._process_healing,
            'applydebuff': self.__process_event,
            'refreshdebuff': self.__process_event
        }.get(event.event_type, __dummy)(event)

    def _process_damage(self, event: ThreatEvent):
        self.total_damage += event.amount
        return event.calculate_threat(self.player_class, self.feral_instinct_points)

    def __process_event(self, event: ThreatEvent):
        return event.calculate_threat(self.player_class, self.feral_instinct_points)

    def _process_rage(self, event: ThreatEvent):
        self.rage_gains += event.amount
        return event.calculate_threat(self.player_class, self.feral_instinct_points)

    def _process_healing(self, event: ThreatEvent):
        self.hp_gains += event.amount
        return event.calculate_threat(self.player_class, self.feral_instinct_points)


class DruidThreatResult(DruidThreatCalculationRequest):
    total_threat: float = 0
    total_threat_feral_instinct: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0
