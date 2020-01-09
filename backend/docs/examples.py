CALC_RESP_EXAMPLE = """{
  "Magmadar": {
    "shield_slam_count": 0,
    "bt_count": 11,
    "revenge_count": 8,
    "hs_count": 33,
    "sunder_count": 16,
    "execute_dmg": 0,
    "goa_procs": 0,
    "rage_gains": 125,
    "time": 70.484,
    "total_damage": 25982,
    "t1_set": False,
    "defiance_points": 5,
    "cleave_count": 0,
    "bs_casts": 0,
    "demo_casts": 1,
    "thunderclap_casts": 0,
    "hp_gains": 600,
    "friendlies_in_combat": 1,
    "enemies_in_combat": 1,
    "player_name": "Aemin",
    "player_class": "Warrior",
    "boss_name": "Magmadar",
    "boss_id": 12,
    "realm": "Skeram",
    "total_threat": 38431,
    "total_threat_defiance": 56071.47,
    "unmodified_tps": 545.2443107655639,
    "tps": 808.644089438738,
  }
}"""

THREAT_RESP_EXAMPLE = """[
  {
    "name": "BattleShout",
    "threat_type": "Flat",
    "val": 56
  },
  {
    "name": "Cleave",
    "threat_type": "Flat",
    "val": 100
  },
  {
    "name": "DefensiveStance",
    "threat_type": "Modifier",
    "val": 1.3
  },
  {
    "name": "Defiance0",
    "threat_type": "Modifier",
    "val": 1
  },
  {
    "name": "Defiance1",
    "threat_type": "Modifier",
    "val": 1.03
  },
  {
    "name": "Defiance2",
    "threat_type": "Modifier",
    "val": 1.06
  },
  {
    "name": "Defiance3",
    "threat_type": "Modifier",
    "val": 1.09
  },
  {
    "name": "Defiance4",
    "threat_type": "Modifier",
    "val": 1.12
  },
  {
    "name": "Defiance5",
    "threat_type": "Modifier",
    "val": 1.15
  },
  {
    "name": "DemoShout",
    "threat_type": "Flat",
    "val": 43
  },
  {
    "name": "Execute",
    "threat_type": "Flat",
    "val": 1
  },
  {
    "name": "GiftOfArthas",
    "threat_type": "Flat",
    "val": 90
  },
  {
    "name": "Healing",
    "threat_type": "Flat",
    "val": 0.5
  },
  {
    "name": "HeroicStrike",
    "threat_type": "Flat",
    "val": 145
  },
  {
    "name": "RageGain",
    "threat_type": "Flat",
    "val": 5
  },
  {
    "name": "Revenge",
    "threat_type": "Flat",
    "val": 315
  },
  {
    "name": "ShieldSlam",
    "threat_type": "Flat",
    "val": 250
  },
  {
    "name": "SunderArmor",
    "threat_type": "Flat",
    "val": 261
  },
  {
    "name": "ThunderClap",
    "threat_type": "Flat",
    "val": 104
  },
  {
    "name": "Tier1Bonus",
    "threat_type": "Modifier",
    "val": 1.15
  },
  {
    "name": "Damage",
    "threat_type": "Flat",
    "val": 1
  }
]""",

HEARTBEAT = "{'status': 'OK'}"