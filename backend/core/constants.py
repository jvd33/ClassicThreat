import enum
from pydantic import BaseModel

class GenericObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Threat(BaseModel):
    threat_type: str
    val: float
    ability: str
    comment: str = None


class Spell:
    HeroicStrike8 = 11567
    HeroicStrike9 = 25286
    Revenge5 = 11601
    Revenge6 = 25288
    ShieldSlam = 23925
    Cleave = 20569
    DefensiveStance = 71
    SunderArmor = 11597
    GiftOfArthas = 11371
    RageGain = 101 # Cause WCL says so
    Execute = 20662
    BattleShout6 = 11551
    BattleShout7 = 25289
    ShieldBash = 1672
    ThunderClap = 11581
    Disarm = 676
    DemoShout = 11556
    Hamstring = 7373
    MockingBlow = 20560
    BerserkerStance = 2458
    BattleStance = 2457
    Bloodthirst = 23894


class WarriorThreatValues:
    def __init__(self, hs_rank=11567, revenge_rank=11601):
        pass

    DefensiveStance = {'threat': {'threat_type': 'Modifier', 'val': 1.3}, 'guid': Spell.DefensiveStance}
    SunderArmor = {'threat': {'threat_type': 'Flat', 'val': 261}, 'guid': Spell.SunderArmor}
    ShieldSlam = {'threat': {'threat_type': 'Flat', 'val': 250}, 'guid': Spell.ShieldSlam}
    Revenge5 = {'threat': {'threat_type': 'Flat', 'val': 315}, 'guid': Spell.Revenge5}
    Revenge6 = {'threat': {'threat_type': 'Flat', 'val': 355}, 'guid': Spell.Revenge5}
    HeroicStrike8 = {'threat': {'threat_type': 'Flat', 'val': 145}, 'guid': [Spell.HeroicStrike8]}
    HeroicStrike9 = {'threat': {'threat_type': 'Flat', 'val': 175}, 'guid': [Spell.HeroicStrike9]}
    GiftOfArthas = {'threat': {'threat_type': 'Flat', 'val': 90}, 'guid': [Spell.GiftOfArthas]}
    RageGain = {'threat': {'threat_type': 'Flat', 'val': 5}, 'guid': [Spell.RageGain]}
    Defiance0 = {'threat': {'threat_type': 'Modifier', 'val': 1}, 'guid': []}
    Defiance1 = {'threat': {'threat_type': 'Modifier', 'val': 1.03}, 'guid': []}
    Defiance2 = {'threat': {'threat_type': 'Modifier', 'val': 1.06} ,'guid': []}
    Defiance3 = {'threat': {'threat_type': 'Modifier', 'val': 1.09}, 'guid': []}
    Defiance4 = {'threat': {'threat_type': 'Modifier', 'val': 1.12} ,'guid': []}
    Defiance5 = {'threat': {'threat_type': 'Modifier', 'val': 1.15}, 'guid': []}
    Healing = {'threat': {'threat_type': 'Flat', 'val': .5}, 'guid': []}
    DemoShout = {'threat': {'threat_type': 'Flat', 'val': 43}, 'guid': [Spell.DemoShout]}
    ThunderClap = {'threat': {'threat_type': 'Flat', 'val': 130}, 'guid': [Spell.ThunderClap]}
    BattleShout6 ={'threat':  {'threat_type': 'Flat', 'val': 56}, 'guid': [Spell.BattleShout6]}
    BattleShout7 ={'threat':  {'threat_type': 'Flat', 'val': 70}, 'guid': [Spell.BattleShout7]} # Not sure if it is actually 70 threat, we'll see 
    Tier1Bonus = {'threat': {'threat_type': 'Modifier', 'val': 1.15}, 'guid': []}
    Execute = {'threat': {'threat_type': 'Flat', 'val': 1}, 'guid': [Spell.Execute]}
    Cleave = {'threat': {'threat_type': 'Flat', 'val': 100}, 'guid': [Spell.Cleave]}
    ShieldBash = {'threat': {'threat_type': 'Flat', 'val': 180}, 'guid': [Spell.ShieldBash]}
    Hamstring = {'threat': {'threat_type': 'Flat', 'val': 141}, 'guid': [Spell.Hamstring]}
    MockingBlow = {'threat': {'threat_type': 'Flat', 'val': 250}, 'guid': [Spell.MockingBlow]} # From libthreat 2, is it really 250?
    Disarm = {'threat': {'threat_type': 'Flat', 'val': 104}, 'guid': [Spell.Disarm]}

    @staticmethod
    def vals(hs_rank=Spell.HeroicStrike8, revenge_rank=Spell.Revenge5, battleshout_rank=Spell.BattleShout6):
        ret = GenericObject(**{attr: getattr(WarriorThreatValues, attr).get('threat').get('val') for attr in dir(WarriorThreatValues)
                if not callable(getattr(WarriorThreatValues, attr)) and not attr.startswith("__")})
        ret.HeroicStrike = WarriorThreatValues.HeroicStrike8.get('threat').get('val') if hs_rank == Spell.HeroicStrike8 \
                                else WarriorThreatValues.HeroicStrike9.get('threat').get('val')
        ret.BattleShout = WarriorThreatValues.BattleShout6.get('threat').get('val') if battleshout_rank == Spell.BattleShout6 \
                                else WarriorThreatValues.BattleShout7.get('threat').get('val')
        ret.Revenge = WarriorThreatValues.Revenge5.get('threat').get('val') if revenge_rank == Spell.Revenge5 \
                                else WarriorThreatValues.Revenge6.get('threat').get('val')
        return ret

    @staticmethod
    def items():
        return [{'name': attr, 'val': getattr(WarriorThreatValues, attr).get('threat')} for attr in dir(WarriorThreatValues)
                if not callable(getattr(WarriorThreatValues, attr)) and not attr.startswith("__")]
