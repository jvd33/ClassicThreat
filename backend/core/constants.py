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
    GiftOfArthas = 11374
    RageGain = 101 # Cause WCL says so
    Execute = 20647
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
    BearForm = 9634
    CatForm = 768
    DemoRoar = 9898
    Cower = 9892
    FaerieFire = 9907
    FaerieFireFeral = 17392
    Swipe = 9908
    Maul = 9881
    Growl = 6795
    HumanoidForm = -1
    FrenziedRegen = 22896
    Shred = 9830
    Rake = 9904
    FerociousBite = [31018, 22829]
    Regrowth = [9858, 9857, 9856, 8941, 8940, 8939, 8938, 8936]
    Rejuvenation = [25299, 774, 1058, 1430, 2090, 2091, 3627, 8910, 9839, 9840, 9841, ] 
    HealingTouch = [5185, 5186, 5187, 5188, 5189, 6778, 8903, 9758, 9888, 9889, 25297]
    Moonfire = [8921, 8924, 8925, 8926, 8927, 8928, 8929, 9833, 9834, 9835]
    Wrath = [5176, 5177, 5178, 5179, 5180, 8905, 9912]
    Starfire = [2912, 8949, 8950, 8951, 9875, 9876, 25298]
    BerserkerRage = 18499
    Intercept = 20617
    Pummel = 6554
    Recklessness = 1719
    Whirlwind = 1680
    Overpower = 11585
    Charge = 11578
    Retaliation = 20230
    ShieldBlock = 2565
    ShieldWall = 871
    Taunt = 355
            


    


class WarriorThreatValues:
    DefensiveStance = {'threat': {'threat_type': 'Modifier', 'val': 1.3}, 'guid': Spell.DefensiveStance}
    BerserkerStance = {'threat': {'threat_type': 'Modifier', 'val': .8}, 'guid': Spell.BerserkerStance}
    BattleStance = {'threat': {'threat_type': 'Modifier', 'val': .8}, 'guid': Spell.BattleStance}

    SunderArmor = {'threat': {'threat_type': 'Flat', 'val': 261}, 'guid': Spell.SunderArmor}
    ShieldSlam = {'threat': {'threat_type': 'Flat', 'val': 250}, 'guid': Spell.ShieldSlam}
    Revenge5 = {'threat': {'threat_type': 'Flat', 'val': 315}, 'guid': Spell.Revenge5}
    Revenge6 = {'threat': {'threat_type': 'Flat', 'val': 355}, 'guid': Spell.Revenge5}
    HeroicStrike8 = {'threat': {'threat_type': 'Flat', 'val': 145}, 'guid': Spell.HeroicStrike8}
    HeroicStrike9 = {'threat': {'threat_type': 'Flat', 'val': 175}, 'guid': Spell.HeroicStrike9}
    GiftOfArthas = {'threat': {'threat_type': 'Flat', 'val': 90}, 'guid': Spell.GiftOfArthas}
    RageGain = {'threat': {'threat_type': 'Flat', 'val': 5}, 'guid': Spell.RageGain}
    Defiance0 = {'threat': {'threat_type': 'Modifier', 'val': 1}, 'guid': None}
    Defiance1 = {'threat': {'threat_type': 'Modifier', 'val': 1.03}, 'guid': None}
    Defiance2 = {'threat': {'threat_type': 'Modifier', 'val': 1.06} ,'guid': None}
    Defiance3 = {'threat': {'threat_type': 'Modifier', 'val': 1.09}, 'guid': None}
    Defiance4 = {'threat': {'threat_type': 'Modifier', 'val': 1.12} ,'guid': None}
    Defiance5 = {'threat': {'threat_type': 'Modifier', 'val': 1.15}, 'guid': None}
    Healing = {'threat': {'threat_type': 'Flat', 'val': .5}, 'guid': None}
    DemoShout = {'threat': {'threat_type': 'Flat', 'val': 43}, 'guid': Spell.DemoShout}
    ThunderClap = {'threat': {'threat_type': 'Flat', 'val': 130}, 'guid': Spell.ThunderClap}
    BattleShout6 ={'threat':  {'threat_type': 'Flat', 'val': 56}, 'guid': Spell.BattleShout6}
    BattleShout7 ={'threat':  {'threat_type': 'Flat', 'val': 70}, 'guid': Spell.BattleShout7} # Not sure if it is actually 70 threat, we'll see 
    Tier1Bonus = {'threat': {'threat_type': 'Modifier', 'val': 1.15}, 'guid': None}
    Execute = {'threat': {'threat_type': 'Flat', 'val': 1}, 'guid': Spell.Execute}
    Cleave = {'threat': {'threat_type': 'Flat', 'val': 100}, 'guid': Spell.Cleave}
    ShieldBash = {'threat': {'threat_type': 'Flat', 'val': 180}, 'guid': Spell.ShieldBash}
    Hamstring = {'threat': {'threat_type': 'Flat', 'val': 145}, 'guid': Spell.Hamstring}
    MockingBlow = {'threat': {'threat_type': 'Flat', 'val': 250}, 'guid': Spell.MockingBlow} # From libthreat 2, is it really 250?
    Disarm = {'threat': {'threat_type': 'Flat', 'val': 104}, 'guid': Spell.Disarm}

    @staticmethod
    def vals():
        ret = GenericObject(**{attr: getattr(WarriorThreatValues, attr).get('threat').get('val') for attr in dir(WarriorThreatValues)
                if not callable(getattr(WarriorThreatValues, attr)) and not attr.startswith("__")})
        return ret

    @staticmethod
    def items():
        return [{'name': attr, 'val': getattr(WarriorThreatValues, attr).get('threat')} for attr in dir(WarriorThreatValues)
                if not callable(getattr(WarriorThreatValues, attr)) and not attr.startswith("__")]


class DruidThreatValues:

    BearForm = {'threat': {'threat_type': 'Modifier', 'val': 1.3}, 'guid': Spell.BearForm}
    CatForm = {'threat': {'threat_type': 'Modifier', 'val': .71}, 'guid': Spell.CatForm}
    Cower = {'threat': {'threat_type': 'Flat', 'val': -600}, 'guid': Spell.Cower}
    FaerieFire = {'threat': {'threat_type': 'Flat', 'val': 108}, 'guid': Spell.FaerieFire}
    FaerieFireFeral = {'threat': {'threat_type': 'Flat', 'val': 108}, 'guid': Spell.FaerieFireFeral}
    Swipe = {'threat': {'threat_type': 'Modifier', 'val': 1.75}, 'guid': Spell.Swipe}
    Maul = {'threat': {'threat_type': 'Modifier', 'val': 1.75}, 'guid': Spell.Maul}

    GiftOfArthas = {'threat': {'threat_type': 'Flat', 'val': 90}, 'guid': Spell.GiftOfArthas}
    RageGain = {'threat': {'threat_type': 'Flat', 'val': 5}, 'guid': Spell.RageGain}
    FeralInstinct0 = {'threat': {'threat_type': 'Modifier', 'val': 0.0}, 'guid': None}
    FeralInstinct1 = {'threat': {'threat_type': 'Modifier', 'val': .03}, 'guid': None}
    FeralInstinct2 = {'threat': {'threat_type': 'Modifier', 'val': .06} ,'guid': None}
    FeralInstinct3 = {'threat': {'threat_type': 'Modifier', 'val': .09}, 'guid': None}
    FeralInstinct4 = {'threat': {'threat_type': 'Modifier', 'val': .12} ,'guid': None}
    FeralInstinct5 = {'threat': {'threat_type': 'Modifier', 'val': .15}, 'guid': None}
    Healing = {'threat': {'threat_type': 'Flat', 'val': .5}, 'guid': None}
    DemoRoar = {'threat': {'threat_type': 'Flat', 'val': 39}, 'guid': Spell.DemoRoar}

    

    @staticmethod
    def vals():
        ret = GenericObject(**{attr: getattr(DruidThreatValues, attr).get('threat').get('val') for attr in dir(DruidThreatValues)
                if not callable(getattr(DruidThreatValues, attr)) and not attr.startswith("__")})
        return ret

    @staticmethod
    def items():
        return [{'name': attr, 'val': getattr(DruidThreatValues, attr).get('threat')} for attr in dir(DruidThreatValues)
                if not callable(getattr(DruidThreatValues, attr)) and not attr.startswith("__")]
