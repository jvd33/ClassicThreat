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
    Thunderfury = 21992


    # Paladin, ugh so many ranks
    RighteousFury = 25780
    HolyLight = [635, 639, 647, 1026, 1042, 3472, 10328, 10329, 25292]
    HolyShock = [25903, 25913, 25914]
    LayOnHands = [633, 2800, 10310]        
    SealOfLight = [20165, 20347, 20348, 20349]
    SealOfWisdom = [20166, 20356, 20357]
    SealOfRighteousness = [20154, 21084, 20287, 20288, 20290, 20291, 20292, 20293, 20289]
    JudgementOfWisdom = [20354, 20186, 20355]
    JudgementOfRighteousness = [20283, 20187, 20280, 20281, 20282, 20284, 20285, 20286]
    JudgementOfLight = [20344, 20185, 20345, 20346]
    FlashOfLight = [19750, 19939, 19940, 19941, 19942, 19943]
    Consecration = [26573, 20924, 20922, 20116, 20923]
    RetributionAura = [7294, 10301, 10300, 10298, 10299]
    Cleanse = 4987
    HolyShield1 = 20925
    HolyShield2 = 20927
    HolyShield3 = 20928

    # Light
    BlessingOfLight1 = 19977
    BlessingOfLight2 = 19978
    BlessingOfLight3 = 19979

    # Might
    BlessingOfMight1 = 19740
    BlessingOfMight2 = 19834
    BlessingOfMight3 = 19835
    BlessingOfMight4 = 19836
    BlessingOfMight5 = 19837
    BlessingOfMight6 = 19838
    BlessingOfMight7 = 25291

    # Sanctuary
    BlessingOfSanctuary1 = 20911
    BlessingOfSanctuary2 = 20912
    BlessingOfSanctuary3 = 20913
    BlessingOfSanctuary4 = 20914

    # Salv
    BlessingOfSalvation = 1038

    # Freedom
    BlessingOfFreedom = 1044

    # BoP
    BlessingOfProtection1 = 1022
    BlessingOfProtection2 = 5599 
    BlessingOfProtection3 = 10278

    # Sac
    BlessingOfSacrifice1 = 6940 
    BlessingOfSacrifice2 = 20729

    # Greater Light
    GreaterBlessingOfLight = 25890

    # Greater Might
    GreaterBlessingOfMight1 = 25782
    GreaterBlessingOfMight2 = 25916

    # Greater Sanctuary
    GreaterBlessingOfSanctuary = 25899

    # Greater Salv
    GreaterBlessingOfSalvation = 25895

    BlessingOfKings = 20217
    GreaterBlessingOfKings = 25898

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
    Thunderfury = {'threat': {'threat_type': 'Flat', 'val': 235}, 'guid': Spell.Thunderfury}

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



class PaladinThreatValues:
    GiftOfArthas = {'threat': {'threat_type': 'Flat', 'val': 90}, 'guid': Spell.GiftOfArthas}
    ManaGain = {'threat': {'threat_type': 'Flat', 'val': .5}, 'guid': None}
    RighteousFury = {'threat': {'threat_type': 'Modifier', 'val': 1.6}, 'guid': None}
    ImpRf0 = {'threat': {'threat_type': 'Modifier', 'val': 1.6}, 'guid': None}
    ImpRf1 = {'threat': {'threat_type': 'Modifier', 'val': 1.7}, 'guid': None}
    ImpRf2 = {'threat': {'threat_type': 'Modifier', 'val': 1.8}, 'guid': None}
    ImpRf3 = {'threat': {'threat_type': 'Modifier', 'val': 1.9}, 'guid': None}
    PaladinSpellHealing = {'threat': {'threat_type': 'Modifier', 'val': .25}, 'guid': None}
    Healing = {'threat': {'threat_type': 'Flat', 'val': .5}, 'guid': None}
    Cleanse = {'threat': {'threat_type': 'Flat', 'val': 40}, 'guid': Spell.Cleanse}
    HolyShield1 = {'threat': {'threat_type': 'Flat', 'val': 20}, 'guid': Spell.HolyShield1}
    HolyShield2 = {'threat': {'threat_type': 'Flat', 'val': 30}, 'guid': Spell.HolyShield2}
    HolyShield3 = {'threat': {'threat_type': 'Flat', 'val': 40}, 'guid': Spell.HolyShield3}

    # Light
    BlessingOfLight1 = {'threat': {'threat_type': 'Flat', 'val': 40}, 'guid': Spell.BlessingOfLight1}
    BlessingOfLight2 = {'threat': {'threat_type': 'Flat', 'val': 50}, 'guid': Spell.BlessingOfLight2}
    BlessingOfLight3 = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.BlessingOfLight3}

    # Might
    BlessingOfMight1 = {'threat': {'threat_type': 'Flat', 'val': 4}, 'guid': Spell.BlessingOfMight1}
    BlessingOfMight2 = {'threat': {'threat_type': 'Flat', 'val': 12}, 'guid': Spell.BlessingOfMight2}
    BlessingOfMight3 = {'threat': {'threat_type': 'Flat', 'val': 22}, 'guid': Spell.BlessingOfMight3}
    BlessingOfMight4 = {'threat': {'threat_type': 'Flat', 'val': 32}, 'guid': Spell.BlessingOfMight4}
    BlessingOfMight5 = {'threat': {'threat_type': 'Flat', 'val': 42}, 'guid': Spell.BlessingOfMight5}
    BlessingOfMight6 = {'threat': {'threat_type': 'Flat', 'val': 52}, 'guid': Spell.BlessingOfMight6}
    BlessingOfMight7 = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.BlessingOfMight7}

    # Sanctuary
    BlessingOfSanctuary1 = {'threat': {'threat_type': 'Flat', 'val': 30}, 'guid': Spell.BlessingOfSanctuary1}
    BlessingOfSanctuary2 = {'threat': {'threat_type': 'Flat', 'val': 40}, 'guid': Spell.BlessingOfSanctuary2}
    BlessingOfSanctuary3 = {'threat': {'threat_type': 'Flat', 'val': 50}, 'guid': Spell.BlessingOfSanctuary3}
    BlessingOfSanctuary4 = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.BlessingOfSanctuary4}

    # Salv
    BlessingOfSalvation = {'threat': {'threat_type': 'Flat', 'val': 26}, 'guid': Spell.BlessingOfSalvation}

    # Freedom
    BlessingOfFreedom = {'threat': {'threat_type': 'Flat', 'val': 18}, 'guid': Spell.BlessingOfFreedom}

    # BoP
    BlessingOfProtection1 = {'threat': {'threat_type': 'Flat', 'val': 10}, 'guid': Spell.BlessingOfProtection1}
    BlessingOfProtection2 = {'threat': {'threat_type': 'Flat', 'val': 24}, 'guid': Spell.BlessingOfProtection2} 
    BlessingOfProtection3 = {'threat': {'threat_type': 'Flat', 'val': 38}, 'guid': Spell.BlessingOfProtection3}

    # Sac
    BlessingOfSacrifice1 = {'threat': {'threat_type': 'Flat', 'val': 46}, 'guid': Spell.BlessingOfSacrifice1} 
    BlessingOfSacrifice2 = {'threat': {'threat_type': 'Flat', 'val': 54}, 'guid': Spell.BlessingOfSacrifice2}

    # Greater Light
    GreaterBlessingOfLight = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.GreaterBlessingOfLight}

    # Greater Might
    GreaterBlessingOfMight1 = {'threat': {'threat_type': 'Flat', 'val': 52}, 'guid': Spell.GreaterBlessingOfMight1}
    GreaterBlessingOfMight2 = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.GreaterBlessingOfMight2}

    # Greater Sanctuary
    GreaterBlessingOfSanctuary = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.GreaterBlessingOfSanctuary}

    # Greater Salv
    GreaterBlessingOfSalvation = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.GreaterBlessingOfSalvation}

    BlessingOfKings = {'threat': {'threat_type': 'Flat', 'val': 20}, 'guid': Spell.BlessingOfKings}
    GreaterBlessingOfKings = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': Spell.GreaterBlessingOfKings}

    # Seals
    SealOfLight1 = {'threat': {'threat_type': 'Flat', 'val': 30}, 'guid': 20165}
    SealOfLight2 = {'threat': {'threat_type': 'Flat', 'val': 40}, 'guid': 20347}
    SealOfLight3 = {'threat': {'threat_type': 'Flat', 'val': 50}, 'guid': 20348}
    SealOfLight4 = {'threat': {'threat_type': 'Flat', 'val': 60}, 'guid': 20349}

    SealOfWisdom1 = {'threat': {'threat_type': 'Flat', 'val': 38}, 'guid': 20166}
    SealOfWisdom2 = {'threat': {'threat_type': 'Flat', 'val': 48}, 'guid': 20356}
    SealOfWisdom3 = {'threat': {'threat_type': 'Flat', 'val': 58}, 'guid': 20357}

    SealOfRighteousness1 = {'threat': {'threat_type': 'Flat', 'val': 1}, 'guid': 21084}
    SealOfRighteousness2 = {'threat': {'threat_type': 'Flat', 'val': 10}, 'guid': 20287}
    SealOfRighteousness3 = {'threat': {'threat_type': 'Flat', 'val': 18}, 'guid': 20288}
    SealOfRighteousness4 = {'threat': {'threat_type': 'Flat', 'val': 26}, 'guid': 20289}
    SealOfRighteousness5 = {'threat': {'threat_type': 'Flat', 'val': 34}, 'guid': 20290}
    SealOfRighteousness6 = {'threat': {'threat_type': 'Flat', 'val': 42}, 'guid': 20291}
    SealOfRighteousness7 = {'threat': {'threat_type': 'Flat', 'val': 50}, 'guid': 20292}
    SealOfRighteousness8 = {'threat': {'threat_type': 'Flat', 'val': 58}, 'guid': 20293}
    Thunderfury = {'threat': {'threat_type': 'Flat', 'val': 235}, 'guid': Spell.Thunderfury}



    @staticmethod
    def vals():
        ret = GenericObject(**{attr: getattr(PaladinThreatValues, attr).get('threat').get('val') for attr in dir(PaladinThreatValues)
                if not callable(getattr(PaladinThreatValues, attr)) and not attr.startswith("__")})
        return ret

    @staticmethod
    def items():
        return [{'name': attr, 'val': getattr(PaladinThreatValues, attr).get('threat')} for attr in dir(PaladinThreatValues)
                if not callable(getattr(PaladinThreatValues, attr)) and not attr.startswith("__")]



FORMS = [Spell.BearForm, Spell.CatForm, Spell.BerserkerStance, Spell.BattleStance, Spell.DefensiveStance]
DAMAGE = [
    Spell.HeroicStrike8, Spell.HeroicStrike9, Spell.Revenge6, Spell.Revenge5, Spell.MockingBlow, Spell.ShieldSlam, 
    Spell.Swipe, Spell.Maul, Spell.FaerieFire, Spell.FaerieFireFeral, Spell.Cleave, Spell.Execute, Spell.ShieldBash,
    Spell.Hamstring, Spell.ThunderClap,
]

GBLESSINGS = [
    Spell.GreaterBlessingOfKings, Spell.GreaterBlessingOfLight, Spell.GreaterBlessingOfMight1, 
    Spell.GreaterBlessingOfMight2, Spell.GreaterBlessingOfSalvation, Spell.GreaterBlessingOfSanctuary
]

BLESSINGS = [
    Spell.BlessingOfFreedom, Spell.BlessingOfKings, Spell.BlessingOfLight1, Spell.BlessingOfLight2, 
    Spell.BlessingOfLight3, Spell.BlessingOfMight1, Spell.BlessingOfMight2, Spell.BlessingOfMight3,
    Spell.BlessingOfMight4, Spell.BlessingOfMight5, Spell.BlessingOfMight6, Spell.BlessingOfMight7,
    Spell.BlessingOfProtection1, Spell.BlessingOfProtection2, Spell.BlessingOfProtection3, 
    Spell.BlessingOfSacrifice1, Spell.BlessingOfSacrifice2, Spell.BlessingOfSalvation,
    Spell.BlessingOfSanctuary1, Spell.BlessingOfSanctuary2, Spell.BlessingOfSanctuary3,
    Spell.BlessingOfSanctuary4, 
]

SEALS = [
    *Spell.SealOfLight, *Spell.SealOfRighteousness, *Spell.SealOfWisdom
]

PALADIN = [
    *GBLESSINGS, *BLESSINGS, *Spell.HolyLight, *Spell.FlashOfLight, *Spell.LayOnHands, Spell.Cleanse,
    *Spell.SealOfLight, *Spell.HolyShock, Spell.HolyShield1, Spell.HolyShield2, Spell.HolyShield3, 
    *Spell.SealOfLight, *Spell.SealOfRighteousness, *Spell.SealOfWisdom, *Spell.JudgementOfRighteousness,
    *Spell.JudgementOfLight, *Spell.JudgementOfWisdom, *Spell.RetributionAura, *Spell.Consecration, *SEALS
]