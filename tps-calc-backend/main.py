import asyncio

from core.models import ThreatCalculationRequest
from core.wcl_service import WCLService

def test():
    req = ThreatCalculationRequest(
        shield_slam_count=9,
        revenge_count=7,
        hs_count=19,
        sunder_count=11,
        execute_dmg=0,
        goa_procs=12,
        rage_gains=114,
        t1_set=False,
        defiance_points=5,
        total_damage=20100,
        time=63,
    )

    threat = req.calculate_threat()
    print(threat)

async def main():
    wcl = WCLService()

    resp = await wcl.get_full_report('pYND7Hcwtfk62LW9')
    print(resp)
    bosses = [f for f in resp.get('fights') if f.get('boss') != 0]
    players = [p for p in resp.get('friendlies')]
    print(bosses)
    print(players)

asyncio.run(main())