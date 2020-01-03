import enum
from pydantic import BaseModel

class GenericObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class ThreatValues:
    DefensiveStance = {'threat_type': 'Modifier', 'val': 1.3}
    SunderArmor = {'threat_type': 'Flat', 'val': 261}
    ShieldSlam = {'threat_type': 'Flat', 'val': 250}
    Revenge = {'threat_type': 'Flat', 'val': 315}
    HeroicStrike = {'threat_type': 'Flat', 'val': 145}
    GiftOfArthas = {'threat_type': 'Flat', 'val': 90}
    RageGain = {'threat_type': 'Flat', 'val': 5}
    Defiance0 = {'threat_type': 'Modifier', 'val': 1}
    Defiance1 = {'threat_type': 'Modifier', 'val': 1.03}
    Defiance2 = {'threat_type': 'Modifier', 'val': 1.06}
    Defiance3 = {'threat_type': 'Modifier', 'val': 1.09}
    Defiance4 = {'threat_type': 'Modifier', 'val': 1.12}
    Defiance5 = {'threat_type': 'Modifier', 'val': 1.15}
    Healing = {'threat_type': 'Flat', 'val': .5}
    DemoShout = {'threat_type': 'Flat', 'val': 45}
    ThunderClap = {'threat_type': 'Flat', 'val': 314*.8}
    BattleShout = {'threat_type': 'Flat', 'val': 56}
    Tier1Bonus = {'threat_type': 'Modifier', 'val': 1.15}
    Execute = {'threat_type': 'Modifier', 'val': 1}

    @staticmethod
    def vals():
        return GenericObject(**{attr: getattr(ThreatValues, attr).get('val') for attr in dir(ThreatValues)
                if not callable(getattr(ThreatValues, attr)) and not attr.startswith("__")})

    @staticmethod
    def items():
        return [{'name': attr, 'val': getattr(ThreatValues, attr)} for attr in dir(ThreatValues)
                if not callable(getattr(ThreatValues, attr)) and not attr.startswith("__")]

class Threat(BaseModel):
    threat_type: str
    val: float
    ability: str
    comment: str = None
