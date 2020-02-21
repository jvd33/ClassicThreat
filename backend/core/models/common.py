from pydantic import BaseModel, AnyUrl, validator
from typing import List, Any, Dict
from collections import defaultdict
from urllib.parse import urlparse

from ..utils import flatten
from ..constants import WarriorThreatValues, Spell, DruidThreatValues, PaladinThreatValues, FORMS, DAMAGE, PALADIN, GBLESSINGS, BLESSINGS, SEALS
    

class EventBreakdown(BaseModel):
    name: str
    guid: int
    count: int = 0
    hits: int = 0
    base_threat: int = 0
    modified_threat: int = 0
    base_tps: int = 0
    modified_tps: int = 0
    percentage_threat: float = 0
    casts_per_minute: float = 0


class WCLDataRequest(BaseModel):
    url: AnyUrl
    player_name: str
    talent_pts: int = None
    bosses: List[str] = []
    friendlies_in_combat: int = 1
    enemies_in_combat: int = 1
    t1_set: bool = False
    include_wipes: bool = True
    
    @validator('url')
    def check_url(cls, v):
        assert v.host == 'classic.warcraftlogs.com' and v.path and len(v.path) > 1 and 'reports' in v.path, \
        "Invalid Log URL."
        return v


    @validator('talent_pts', allow_reuse=True)
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
    execute_percent: float = 0.0
    hs_cpm: float = 0.0


class BossActivityRequest(BaseModel):
    player_id: int
    start_time: int
    end_time: int
    encounter: int
    report_id: str
    boss_name: str
    is_kill: int


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
    hit_type: int = -1
    amount: float = 0
    class_modifier: int = 0
    base_threat: int = 0
    modified_threat: int = 0

    def calculate_threat(self, player_class, talent_pts=5, t1=False):
        mods = {
            'warrior': self.__warr_modifiers,
            'druid': self.__druid_modifiers,
            'paladin': self.__paladin_modifiers,
        }.get(player_class.casefold(), None)
        raw = 0
        if not mods:    
            raise KeyError('Invalid Class Specified')
        if self.guid == Spell.Execute:
            self.base_threat, self.modified_threat = self.amount, self.amount
            return self
            
        if self.event_type == 'cast':
            if self.guid in [Spell.BattleShout6, Spell.BattleShout7]:
                raw = mods.get(self.guid, mods.get('noop'))(self.friendlies_in_combat, self.enemies_in_combat)
            elif self.guid == Spell.SunderArmor:
                raw = mods.get(self.guid, mods.get('noop'))(t1)
            elif self.guid in [*GBLESSINGS, *BLESSINGS]:
                raw = 0
            elif self.guid in SEALS:
                raw = mods.get(self.guid)(self.enemies_in_combat)
            elif self.guid not in [*DAMAGE, *FORMS, Spell.RighteousFury, Spell.HolyShield1, Spell.HolyShield2, Spell.HolyShield3]:
                raw = mods.get(self.guid, mods.get('noop'))

        elif self.event_type == 'damage':
            if self.guid in [Spell.Maul, Spell.Swipe]:
                raw = mods.get(self.guid, mods.get('noop'))(self.amount)
            elif self.guid in DAMAGE and self.hit_type not in [7, 8]:
                raw = mods.get(self.guid, mods.get('noop')) + self.amount
            elif self.guid == Spell.SunderArmor and self.hit_type in [7, 8]:
                raw = mods.get(self.guid, mods.get('noop'))(t1) * -1
            elif self.guid in [Spell.HolyShield1, Spell.HolyShield2, Spell.HolyShield3]:
                raw = mods.get(self.guid) + (self.amount * 1.2)
            elif self.guid == Spell.Thunderfury:
                raw = mods.get(self.guid) + self.amount
            else:
                raw = self.amount

        elif self.event_type == 'heal':
            if self.guid in [*Spell.HolyLight, *Spell.HolyShock, *Spell.FlashOfLight, *Spell.LayOnHands]:
                raw = mods.get('paladinspellhealing')(self.amount, self.enemies_in_combat)
            elif self.guid != 23394: # Shadow of Ebonroc hotfix
                self.name = 'Healing Done'
                self.guid = -100
                raw = mods.get('heal')(self.amount, self.enemies_in_combat)

        elif self.event_type in ['applydebuff', 'refreshdebuff'] and self.guid not in [Spell.SunderArmor, *FORMS, Spell.Thunderfury, *Spell.WisdomGuids]:
            raw = mods.get(self.guid, mods.get('noop'))

        elif self.event_type == 'energize':
            if player_class.casefold() == 'paladin':
                if self.guid in PALADIN:
                    raw = mods.get('judgementenergize')(self.amount)
                elif self.guid in Spell.WisdomGuids: 
                    raw = 0
                else:
                    raw = mods.get('mana')(self.amount)

            elif self.guid in [2687, 23602, 29131, 12964, 17057, 17099, 16959]:
                self.name = 'Resource Gain'
                self.guid = Spell.RageGain
                raw = mods.get(Spell.RageGain)(self.amount)
            elif self.guid == 23513:
                raw = mods.get(Spell.RageGain)(self.amount)
            else:
                raw = mods.get('heal')(self.amount, self.enemies_in_combat)

        elif self.event_type in ['applybuff', 'refreshbuff']:
            if self.guid in [*GBLESSINGS, *BLESSINGS]:
                raw = mods.get(self.guid)(self.enemies_in_combat)

        else:
            raw = 0

        if self.event_type != 'energize' or player_class.casefold() == 'paladin':
            self.modified_threat, self.base_threat = mods.get(self.class_modifier)(raw, talent_pts), raw
            return self

        self.base_threat, self.modified_threat = raw, raw
        return self



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
            Spell.Thunderfury: __t.Thunderfury,
            'heal': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            'noop': 0
        }

    @property
    def __druid_modifiers(self):
        __t = DruidThreatValues.vals()
        return {
            Spell.GiftOfArthas: __t.GiftOfArthas,
            Spell.RageGain: lambda x, __t=__t: x * __t.RageGain,
            'heal': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            Spell.DemoRoar: __t.DemoRoar,
            Spell.BearForm: lambda x, d, __t=__t: x * (__t.BearForm + getattr(__t, f'FeralInstinct{d}')),
            Spell.CatForm: lambda x, d, __t=__t: x * __t.CatForm,
            Spell.Swipe: lambda x, __t=__t: x * __t.Swipe,
            Spell.Maul: lambda x, __t=__t: x * __t.Maul,
            Spell.FaerieFire: __t.FaerieFire,
            Spell.FaerieFireFeral: __t.FaerieFire,
            Spell.Cower: __t.Cower,
            Spell.HumanoidForm: lambda x, d: x * 1,
            'noop': 0
        }

    @property
    def __paladin_modifiers(self):
        __t = PaladinThreatValues.vals()
        return {
            Spell.GiftOfArthas: __t.GiftOfArthas,
            'mana': lambda x, __t=__t: x * __t.ManaGain,
            'paladinspellhealing': lambda x, n, __t=__t: x * __t.PaladinSpellHealing,
            'judgementenergize': lambda x, __t=__t: x * __t.Healing,
            'heal': lambda x, n, __t=__t: x * __t.Healing / n, # Split
            Spell.Cleanse: __t.Cleanse,
            Spell.Thunderfury: __t.Thunderfury,
            Spell.HolyShield1: __t.HolyShield1,
            Spell.HolyShield2: __t.HolyShield2,
            Spell.HolyShield3: __t.HolyShield3,
            Spell.RighteousFury: lambda x, d, __t=__t: x * getattr(__t, f'ImpRf{d}'),
            Spell.BlessingOfLight1: lambda n, __t=__t: __t.BlessingOfLight1/n,
            Spell.BlessingOfLight2: lambda n, __t=__t: __t.BlessingOfLight2/n, 
            Spell.BlessingOfLight3: lambda n, __t=__t: __t.BlessingOfLight3/n, 
            Spell.BlessingOfMight1: lambda n, __t=__t: __t.BlessingOfMight1/n, 
            Spell.BlessingOfMight2: lambda n, __t=__t: __t.BlessingOfMight2/n,
            Spell.BlessingOfMight3: lambda n, __t=__t: __t.BlessingOfMight3/n,
            Spell.BlessingOfMight4: lambda n, __t=__t: __t.BlessingOfMight4/n,
            Spell.BlessingOfMight5: lambda n, __t=__t: __t.BlessingOfMight5/n,
            Spell.BlessingOfMight6: lambda n, __t=__t: __t.BlessingOfMight6/n, 
            Spell.BlessingOfMight7: lambda n, __t=__t: __t.BlessingOfMight7/n, 
            Spell.BlessingOfSanctuary1: lambda n, __t=__t: __t.BlessingOfSanctuary1/n,
            Spell.BlessingOfSanctuary2: lambda n, __t=__t: __t.BlessingOfSanctuary2/n,
            Spell.BlessingOfSanctuary3: lambda n, __t=__t: __t.BlessingOfSanctuary3/n,
            Spell.BlessingOfSanctuary4: lambda n, __t=__t: __t.BlessingOfSanctuary4/n,
            Spell.BlessingOfSalvation: lambda n, __t=__t: __t.BlessingOfSalvation/n,
            Spell.BlessingOfFreedom: lambda n, __t=__t: __t.BlessingOfFreedom,
            Spell.BlessingOfProtection1: lambda n, __t=__t: __t.BlessingOfProtection1,
            Spell.BlessingOfProtection2: lambda n, __t=__t: __t.BlessingOfProtection2,
            Spell.BlessingOfProtection3: lambda n, __t=__t: __t.BlessingOfProtection3,
            Spell.BlessingOfSacrifice1: lambda n, __t=__t: __t.BlessingOfSacrifice1,
            Spell.BlessingOfSacrifice2: lambda n, __t=__t: __t.BlessingOfSacrifice2,
            Spell.GreaterBlessingOfLight: lambda n, __t=__t: __t.GreaterBlessingOfLight/n,
            Spell.GreaterBlessingOfMight1: lambda n, __t=__t: __t.GreaterBlessingOfMight1/n,
            Spell.GreaterBlessingOfMight2: lambda n, __t=__t: __t.GreaterBlessingOfMight2/n,
            Spell.GreaterBlessingOfSanctuary: lambda n, __t=__t: __t.GreaterBlessingOfSanctuary/n,
            Spell.GreaterBlessingOfSalvation: lambda n, __t=__t: __t.GreaterBlessingOfSalvation/n,
            Spell.BlessingOfKings: lambda n, __t=__t: __t.BlessingOfKings,
            Spell.GreaterBlessingOfKings: lambda n, __t=__t: __t.GreaterBlessingOfKings/n,
            20165: lambda n, __t=__t: __t.SealOfLight1/n,
            20347: lambda n, __t=__t: __t.SealOfLight2/n,
            20348: lambda n, __t=__t: __t.SealOfLight3/n,
            20349: lambda n, __t=__t: __t.SealOfLight4/n,

            20166: lambda n, __t=__t: __t.SealOfWisdom1/n,
            20356: lambda n, __t=__t: __t.SealOfWisdom2/n,
            20357: lambda n, __t=__t: __t.SealOfWisdom3/n,

            21084: lambda n, __t=__t: __t.SealOfRighteousness1/n,
            20287: lambda n, __t=__t: __t.SealOfRighteousness2/n,
            20288: lambda n, __t=__t: __t.SealOfRighteousness3/n,
            20289: lambda n, __t=__t: __t.SealOfRighteousness4/n,
            20290: lambda n, __t=__t: __t.SealOfRighteousness5/n,
            20291: lambda n, __t=__t: __t.SealOfRighteousness6/n,
            20292: lambda n, __t=__t: __t.SealOfRighteousness7/n,
            20293: lambda n, __t=__t: __t.SealOfRighteousness8/n,
            'noop': 0
        }


class FightLog(BaseModel):
    boss_name: str
    boss_id: int
    report_id: str
    is_kill: bool
    player_name: str
    player_class: str
    total_time: int
    dps_threat: List = list()
    events: List = list()
    realm: str
    defiance_points: int = 0
    feral_instinct_points: int = 0
    imp_rf_pts: int = 0
    friendlies_in_combat: int = 1
    gear: List = list()
    aggro_windows: Dict = dict()

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
                      is_kill,
                      aggro_windows,
                      t1=False,
                      talent_pts=5,
                      friendlies=1,
                      **kwargs):
        f = FightLog(
            boss_name=boss_name,
            player_name=player_name,
            boss_id=boss_id,
            report_id=report_id,
            total_time=total_time,
            player_class=player_class,
            realm=realm,
            is_kill=is_kill,
            gear=gear or [],
            defiance_points=talent_pts,
            feral_instinct_points=talent_pts,
            imp_rf_pts=talent_pts,
            friendlies_in_combat=friendlies,
            dps_threat=[FuryDPSThreatResult(total_time, **d) for d in dps_threat if d.get('player_name') != player_name],
            aggro_windows=aggro_windows
        )
        if player_class == 'Druid':
            f.defiance_points = 0
            f.imp_rf_pts = 0
        elif player_class == 'Warrior':
            f.feral_instinct_points = 0
            f.imp_rf_pts = 0
        elif player_class == 'Paladin':
            f.feral_instinct_points = 0
            f.defiance_points = 0
        modifier_event = [i for i in modifier_events if i.get('boss_id') == boss_id]
        for event in resp:
            if event.get('type') == 'damage' and event.get('targetIsFriendly', False):
                continue
            e = ThreatEvent(
                name=event.get('ability', {}).get('name', ''),
                guid=event.get('ability', {}).get('guid', 0),
                event_type=event.get('type', 0),
                timestamp=event.get('timestamp', 0),
                hit_type=event.get('hitType', -1),
                amount=event.get('amount') or (event.get('resourceChange', 0) - event.get('waste', 0)) or 0,
                class_modifier=FightLog._get_event_modifier(modifier_event, event, player_class) or 0,
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
            'druid': Spell.BearForm,
            'paladin': Spell.RighteousFury,
        }.get(player_class.casefold())

        if not default:
            raise KeyError('Invalid Player Class')

        time = event.get('timestamp')
        for k, rnges in [el for el in modifier_events[0].items() if el[0] != 'boss_id']:
            for rnge in rnges:
                if rnge[0] <= time and (time <= rnge[1] if rnge[1] else True):
                    return k
        return default
