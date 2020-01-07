<template>
  <q-page>
    <q-list bordered class="rounded-borders border-color-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name">
        <q-card>
          <q-card-section>
            <span class="text-h4 text-weight-bold text-center text-primary">
              {{value.tps.toPrecision(5)}} <span class="text-white">Threat per Second (estimated)</span>
              <br/>
              <br/>
            </span>
            <q-item v-if="value.bt_count > 0" class="q-pa-md">
              <q-item-section class="row"><span class="col-8"><q-icon name="app:bt" class="col-3 q-mr-sm" size="40px"/>
              Bloodthirst Casts Per Minute: <strong>{{(value.bt_count/(value.time/60)).toPrecision(4)}}</strong></span>
              </q-item-section>
            </q-item>
            <q-list elevated dark bordered separator class="q-ma-md">
              <q-item class="q-pa-md" >
                <q-item-section class="row"><span class="col-8"><q-icon name="app:dstance" size="40px" class="col-3 q-mr-sm"/>Total Threat (estimated): <strong>{{value.total_threat_defiance.toPrecision(4)}}</strong></span></q-item-section>
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
            <q-expansion-item flat class="q-pt-lg" icon="" label="DPS Rip Thresholds">
              <q-table
                title=""
                :pagination.sync="threat_pagination"
                dense
                :columns="getThreatTableCols()"
                :data="getThreatTableData(value.tps)"
                row-key="dps"
                hide-header
                hide-bottom
              >
                <template v-slot:body-cell-name="data">
                  <q-td v-bind:class="{ background: data.faction }">
                    <q-icon
                      :name="getIcon(data.player_class)"
                      size="32px"
                      :label="data.player_class"
                      class="q-ma-sm"
                      title=""
                    />
                    <span class="text-right" v-if="!data.tranq || data.faction === 'Alliance'">Rip at: {{data.dps}} DPS (very roughly estimated!)</span>
                    <span class="text-right" v-if="data.tranq && data.faction === 'Horde'">Rip at: {{(data.dps/.7).toPrecision(4)}} DPS (very roughly estimated!)</span>
                    <q-toggle :icon="'app:tranq'" dense v-model="data.tranq" v-if="data.faction === 'Horde'" label="Enable Tranquil Air Totem Modifier?"></q-toggle>
                  </q-td>
                </template>
              </q-table>
            </q-expansion-item>
            <q-expansion-item popup flat default-closed class="bg-primary q-pt-lg" icon="help" label="Raw Data">
                <q-table
                  title=""
                  :pagination.sync="pagination"
                  dense
                  :data="getTableCols(value)"
                  :columns="columns"
                  row-key="name"
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
        'Druid': {mod: .71, rip_at: 1.3},
        'Hunter': {mod: 1, rip_at: 1.3},
      };
      let ret = [];
      Object.keys(classes).forEach((k) => {
          ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/classes[k].mod).toPrecision(4), faction: 'Horde' });
          ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod * .7)).toPrecision(4), faction: 'Alliance' });
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
        { name: 'Player Class', align: 'center', label: 'Player Class', field: 'class', sortable: true },
        { name: 'DPS to Rip Aggro', align: 'center', label: 'DPS to Rip', field: 'dps', sortable: true }
      ],
    }
  },
};
</script>
