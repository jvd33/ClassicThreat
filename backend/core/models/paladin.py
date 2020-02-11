from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import PaladinThreatValues, Spell
from .common import ThreatEvent, FightLog, GBLESSINGS

class PaladinThreatCalculationRequest(BaseModel):

    goa_procs: int = 0
    mana_gains: int = 0
    greater_blessing_casts: int = 0
    greater_blessing_hits: int = 0
    holy_shield_casts: int = 0
    time: float = 0
    total_damage: int = 0
    imp_rf_pts: int = 5
    hp_gains: float = 0
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1 
    player_name: str = None
    player_class: str = None
    boss_name: str = None
    boss_id: int = None
    realm: str = None
    dps_threat: List = list()
    gear: List = list()


    def process_events(self, events: List[ThreatEvent]):
        mapper = defaultdict(int)
        for event in events:
            if event.event_type == 'cast':
                if event.guid in GBLESSINGS:
                    self.greater_blessing_casts += 1
                elif event.guid in [Spell.HolyShield1, Spell.HolyShield2, Spell.HolyShield3]:
                    self.holy_shield_casts += 1
            elif event.event_type == 'energize':
                self.mana_gains += event.amount
            elif event.event_type in ['applybuff', 'refreshbuff']:
                if event.guid in GBLESSINGS:
                    self.greater_blessing_hits += 1

            if event.guid == Spell.GiftOfArthas:
                self.goa_procs += 1

        return mapper

    @staticmethod
    def from_event_log(log: FightLog):
        resp = PaladinThreatCalculationRequest(
            boss_name=log.boss_name,
            boss_id=log.boss_id,
            player_class=log.player_class,
            player_name=log.player_name,
            time=log.total_time / 1000.00,
            realm=log.realm,
            imp_rf_pts=log.imp_rf_pts,
            friendlies_in_combat=log.friendlies_in_combat,
            gear=log.gear,
            dps_threat=log.dps_threat
        )
        total_threat, total_threat_imp_rf, unmodified_tps, tps = [0, 0, 0, 0]
        for event in log.events:
            modified, raw = resp._process_event(event)
            total_threat_imp_rf += modified
            total_threat += raw

        unmodified_tps = total_threat / resp.time
        tps = total_threat_imp_rf / resp.time
        event_data = resp.process_events(log.events)
        return PaladinThreatResult(
            **dict(resp),
            **event_data,
            total_threat=total_threat,
            total_threat_imp_rf=total_threat_imp_rf,
            unmodified_tps=unmodified_tps,
            tps=tps,
        )

        
    def _process_event(self, event: ThreatEvent):
        def __dummy(event: ThreatEvent):
            return 0, 0

        return {
            'damage': self._process_damage,
            'cast': self.__process_event,
            'energize': self.__process_event,
            'heal': self._process_healing,
            'applydebuff': self.__process_event,
            'refreshdebuff': self.__process_event,
            'refreshbuff': self.__process_event,
            'applybuff': self.__process_event,
        }.get(event.event_type, __dummy)(event)

    def _process_damage(self, event: ThreatEvent):
        self.total_damage += event.amount
        return event.calculate_threat(self.player_class, self.imp_rf_pts)

    def _process_healing(self, event: ThreatEvent):
        self.hp_gains += event.amount
        return event.calculate_threat(self.player_class, self.imp_rf_pts)

    def __process_event(self, event: ThreatEvent):
        return event.calculate_threat(self.player_class, self.imp_rf_pts)

class PaladinThreatResult(PaladinThreatCalculationRequest):
    total_threat: float = 0
    total_threat_imp_rf: float = 0
    unmodified_tps: float = 0.0
    tps: float = 0.0
