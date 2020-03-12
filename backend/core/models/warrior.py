from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict

from ..constants import WarriorThreatValues, Spell
from .common import FightLog, ThreatEvent, FuryDPSThreatResult, EventBreakdown


class WarriorThreatCalculationRequest(BaseModel):
    time: float = 0
    total_damage: int = 0
    t1_set: bool = False
    defiance_points: int = 5
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1  # for healing and shout threat
    player_name: str = None
    player_class: str = None
    boss_name: str = None
    boss_id: int = None
    realm: str = None
    events: List[EventBreakdown] = []
    dps_threat: List = list()
    gear: List = list()
    

    def process_events(self, events: List[ThreatEvent]):
        mapper = {}

        for event in events:
            breakdown = mapper.get(event.guid, None)
            if not breakdown: 
                breakdown = EventBreakdown(
                    name=event.name,
                    guid=event.guid,
                    count=0
                )
                mapper[event.guid] = breakdown

            breakdown.base_threat += event.base_threat
            breakdown.modified_threat += event.modified_threat

            if event.event_type == 'cast':
                breakdown.count += 1
                if event.guid == Spell.SunderArmor:
                    breakdown.hits += 1

            if event.event_type == 'damage':
                if event.hit_type not in [7, 8]:
                    breakdown.hits += 1
                else:
                    if event.guid == Spell.SunderArmor:
                        breakdown.hits -= 1

            if event.guid == Spell.GiftOfArthas:
                breakdown.hits += 1

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
            gear=log.gear or [],
            dps_threat=log.dps_threat or [],
        )

        event_times = [e.timestamp for e in log.events] or [0]
        start_active, end_active = min(event_times), max(event_times)
        base_threat, modified_threat, base_tps, modified_tps, threat_with_aggro = [0, 0, 0, 0, 0]
        windows = log.aggro_windows.get('windows')
        time_with_aggro = log.aggro_windows.get('total_time', 0) / 1000.00
        events = []
        for event in log.events:
            event = resp._process_event(event)
            events.append(event)
            modified_threat += event.modified_threat
            base_threat += event.base_threat
            if any(w and w[0] <= event.timestamp <= w[1] for w in windows):
                threat_with_aggro += event.modified_threat

        base_tps = base_threat / resp.time
        modified_tps = modified_threat / resp.time
        event_data = resp.process_events(log.events).values()
        threat_events = [e for e in list(event_data) if e.base_threat > 0]
        active_time = (end_active - start_active) / 1000.00
        for e in threat_events:
            e.base_tps = e.base_tps/resp.time
            e.modified_tps = e.modified_tps/resp.time
            e.percentage_threat = (e.modified_threat/modified_threat) * 100
            e.casts_per_minute = e.count / (resp.time/60)
        resp.events = sorted(threat_events, key=lambda e: e.percentage_threat, reverse=True)
        log.events = events
        return WarriorThreatResult(
            **dict(resp),
            base_threat=base_threat,
            modified_threat=modified_threat,
            threat_with_aggro=threat_with_aggro,
            base_tps=base_tps,
            modified_tps=modified_tps,
            time_with_aggro=time_with_aggro,
            active_time=active_time,
            is_kill=log.is_kill,
            report_id=log.report_id,
        ), log

        
    def _process_event(self, event: ThreatEvent):
        def __dummy(event: ThreatEvent):
            return event

        return {
            'damage': self._process_damage,
            'cast': self.__process_event,
            'energize': self.__process_event,
            'heal': self.__process_event,
            'applydebuff': self.__process_event,
            'refreshdebuff': self.__process_event
        }.get(event.event_type, __dummy)(event)

    def _process_damage(self, event: ThreatEvent):
        self.total_damage += event.amount
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)

    def __process_event(self, event: ThreatEvent):
        return event.calculate_threat(self.player_class, self.defiance_points, self.t1_set)


class WarriorThreatResult(WarriorThreatCalculationRequest):
    base_threat: float = 0
    modified_threat: float = 0
    threat_with_aggro: float = 0
    base_tps: float = 0.0
    modified_tps: float = 0.0
    active_time: float = 0.0
    time_with_aggro: float = 0.0
    is_kill: bool
    report_id: str