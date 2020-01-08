<template>
  <q-page>
    <q-list bordered class="rounded-borders border-color-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name">
        <q-card>
          <q-card-section class="q-pa-sm row-auto">
            <span class="text-h4 text-weight-bold text-center text-primary row-auto">
              {{value.tps.toPrecision(5)}} <span class="text-white">Threat per Second (estimated)</span>
              <br/>
              <br/>
            </span>
            <q-item class="q-pa-md row-auto" >
              <q-list elevated dark bordered separator class="q-ma-md col-6">
                <q-item class="q-pa-md col-6 row-auto" >
                  <q-item-section class="row"><span><q-icon name="app:dstance" size="40px" class="col-3 q-mr-sm"/>Total Threat (estimated): <strong>{{value.total_threat_defiance.toPrecision(8)}}</strong></span></q-item-section>
                </q-item>
                <q-item v-if="value.bt_count > 0" class="q-pa-md">
                  <q-item-section class="row"><span class="col-8"><q-icon name="app:bt" class="col-3 q-mr-sm" size="40px"/>
                  Bloodthirst Casts Per Minute: <strong>{{(value.bt_count/(value.time/60)).toPrecision(4)}}</strong></span>
                  </q-item-section>
                </q-item>
                <q-item v-if="value.shield_slam_count > 0" class="q-pa-md" >
                  <q-item-section class="row">
                    <span class="col-8">
                      <q-icon name="app:ss" size="40px" class="col-3 q-mr-sm"/>
                        Shield Slam Casts Per Minute: <strong>{{(value.shield_slam_count/(value.time/60)).toPrecision(4)}}</strong></span>
                  </q-item-section>
                </q-item>
                <q-item class="q-pa-md" >
                  <q-item-section class="row"><span class="col-8"><q-icon name="app:revenge" size="40px" class="col-3 q-mr-sm"/>
                  Revenge Casts Per Minute: <strong>{{(value.revenge_count/(value.time/60)).toPrecision(4)}}</strong></span></q-item-section>
                </q-item>
                <q-item class="q-pa-md" >
                  <q-item-section class="row"><span class="col-8"><q-icon name="app:sunder" class="col=3 q-mr-sm" size="40px"/>Sunder Armor Hits Per Minute: <strong>{{(value.sunder_count/(value.time/60)).toPrecision(4)}}</strong></span></q-item-section>
                </q-item>
                <q-item class="q-pa-md" >
                  <q-item-section class="row"><span class="col-8"><q-icon name="app:hs" size="40px" class="col-3 q-mr-sm"/>Heroic Strike Casts Per Minute: <strong>{{(value.hs_count/(value.time/60)).toPrecision(4)}}</strong></span></q-item-section>
                </q-item>
                <q-item class="q-pa-md" >
                  <q-item-section class="row"><span class="col-8"><q-icon name="app:taunt" size="40px" class="col-3 q-mr-sm"/>Damage per Second: <strong>{{(value.total_damage/value.time).toPrecision(4)}}</strong></span></q-item-section>
                </q-item>
              </q-list>
              <q-expansion-item flat default-closed class="bg-primary q-ma-lg col-6" label="DPS Rip Thresholds" icon="warning">
                <q-table
                  title=""
                  class="q-ma-md"
                  :pagination.sync="threat_pagination"
                  dense
                  :columns="threatCols"
                  visible-columns="['player_name', 'dps']"
                  :data="getThreatTableData(value.tps)"
                  row-key="player_class"
                  hide-bottom
                >
                  <template v-slot:body-cell-name="props">
                    <q-td v-bind:class="{ background: props.row.faction }" :props="props">
                      <q-icon
                        :name="getIcon(props.value)"
                        size="20px"
                        :label="props.value"
                        class="q-ma-sm"
                        title=""
                      />
                      <span class="text-right" v-if="!props.row.tranq || props.row.faction === 'Alliance'">Rip at: {{props.row.dps}} DPS (very roughly estimated!)</span>
                      <span class="text-right" v-if="props.row.tranq && props.row.faction === 'Horde'">Rip at: {{(props.row.dps/.7).toPrecision(4)}} DPS (very roughly estimated!)</span>
                      <q-toggle :icon="'app:tranq'" dense v-model="props.row.tranq" v-if="props.row.faction === 'Horde'" label="Enable Tranquil Air Totem Modifier?"></q-toggle>
                    </q-td>
                  </template>
                </q-table>
              </q-expansion-item>
            </q-item>
            <q-expansion-item flat default-closed class="bg-primary q-ma-lg col-6" icon="help" label="Raw Data">
                <q-table
                  title=""
                  :pagination.sync="pagination"
                  dense
                  :data="getTableCols(value)"
                  :columns="columns"
                  row-key="name"
                  class="q-ma-md"
                  hide-bottom
                />
            </q-expansion-item>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </q-list>
  </q-page>
</template>
<script>
export default {
  name: 'ThreatResult',
  props: ['results'],
  methods: {
    getIcon(ability) {
      if (ability.includes('Defiance')) return 'app:defiance';
      switch(ability) {
        case 'Bloodthirst': return 'app:bt';
        case 'Shield Slam': return 'app:ss';
        case 'Heroic Strike': return 'app:hs';
        case 'Defensive Stance': return 'app:dstance';
        case 'Sunder Armor': return 'app:sunder';
        case 'Demo Shout': return 'app:demo';
        case 'Battle Shout': return 'app:bs';
        case 'Rage Gain': return 'app:rage';
        case 'Thunder Clap': return 'app:tc';
        case 'Execute': return 'app:execute';
        case 'Gift Of Arthas': return 'app:goa';
        case 'Healing': return 'app:heals';
        case 'Tier1 Bonus': return 'app:t1';
        case 'Revenge': return 'app:revenge';
        case 'Warrior': return 'app:warr';
        case 'Mage': return 'app:mage';
        case 'Warlock (with imp)': return 'app:warlock';
        case 'Rogue': return 'app:rogue';
        case 'Druid': return 'app:druid';
        case 'Hunter': return 'app:hunter';
        case 'Cleave': return 'app:cleave';
        default: return ability;
      };
    },
    getTableCols(data) {
      let ret = [];
      for (const prop in data) {
        ret.push({'name': prop, 'value': data[prop]});
      }
      return ret;
    },
    getThreatTableData(tps) {
      let classes = {
        'Warrior': {mod: .8, rip_at: 1.1},
        'Mage': {mod: .7, rip_at: 1.3},
        'Warlock (with imp)': {mod: .8, rip_at: 1.3},
        'Rogue': {mod: .71, rip_at: 1.1},
        'Druid': {mod: .71, rip_at: 1.1},
        'Hunter': {mod: 1, rip_at: 1.3},
      };
      let ret = [];
      Object.keys(classes).forEach((k) => {
          ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/classes[k].mod).toPrecision(4), faction: 'Horde', tranq: false });
          ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod * .7)).toPrecision(4), faction: 'Alliance', tranq: false });
      });
      return ret;
    },
  },
  data () {
    return {
      name: 'RawResults',
      errorState: false,
      errorMsg: null,
      pagination: {
        sortBy: 'name',
        rowsPerPage: 0,
      },
      threat_pagination: {
        sortBy: 'faction',
        descending: false,
        rowsPerPage: 0,
      },
      columns: [
        { name: 'Metric', align: 'center', label: 'Metric', field: 'name', sortable: true },
        { name: 'Metric Value', align: 'center', label: 'Metric Value', field: 'value', sortable: true },
      ],
      threatCols:  [
        { name: 'Player Class', align: 'center', label: 'Player Class', field: 'player_class', sortable: false },
        { name: 'DPS to Rip Aggro', align: 'center', label: 'DPS to Rip', field: 'dps', sortable: false },
      ],
    }
  },
};
</script>
