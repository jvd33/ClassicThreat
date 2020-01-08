<template>
  <q-page>
    <q-list bordered class="rounded-borders border-color-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name">
        <q-card class="qa-pa-md doc-container">
          <q-card-section class="q-pa-sm row col-12 justify-start">
            <span class="text-h4 text-weight-bold text-center text-primary col q-pa-md">
              <strong class="text-primary">{{value.tps.toPrecision(5)}}</strong> Threat per Second (estimated)
              <br/>
              <br/>
            </span>
            <q-item class="row-12 no-wrap">
              <q-list elevated dark bordered separator class="q-ma-sm col-4 justify-around">
                <q-item class="q-pa-md" >
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

              <q-expansion-item
                default-opened
                flat header-class="bg-primary"
                class="q-ma-md col-6 justify-around"
                label="DPS Rip Thresholds"
                icon="warning"
                disable="true"
                expand-icon-class=""
              >
                <q-tabs
                  v-model="tab"
                  dense
                  align="justify"
                >
                  <q-tab name="value.name + '_horde'" icon="app:horde" />
                  <q-tab name="value.name + '_alliance'" icon="app:alliance" />
                </q-tabs>
                <q-tab-panels v-model="tab" animated>
                  <q-tab-panel name="value.name + '_alliance'">
                    <q-table
                      title=""
                      :label="Alliance"
                      class="q-ma-md bg-alliance"
                      :pagination.sync="threat_pagination"
                      dense
                      hide-header
                      :columns="threatCols"
                      visible-columns="['player_class', 'dps']"
                      :data="getThreatTableData(value.tps, 'Alliance')"
                      row-key="name"
                      hide-bottom
                    >
                      <template v-slot:body-cell-name="player_class">
                        <q-td v-bind:class="{ background: props.row.faction }" :props="props">
                          <q-icon
                            :name="getIcon(props.row.player_class)"
                            size="20px"
                            :label="props.row.player_class"
                            class="q-ma-sm"
                            title=""
                          />
                          <span class="text-right">{{props.row.player_class}}</span>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-name="dps">
                        <q-td v-bind:class="{ background: props.row.dps }" :props="props">
                          <span class="text-right">Rip at: {{props.row.dps}} DPS (very roughly estimated!)</span>
                        </q-td>
                      </template>
                    </q-table>
                  </q-tab-panel>
                  <q-tab-panel name="Horde" icon="app:horde">
                    <q-table
                      title=""
                      :label="Horde"
                      class="q-ma-md"
                      :pagination.sync="threat_pagination"
                      dense
                      :columns="threatCols"
                      visible-columns="['player_class', 'dps']"
                      :data="getThreatTableData(value.tps, 'Horde')"
                      row-key="name"
                      hide-header
                      hide-bottom
                    >
                    <template v-slot:top="props">
                      <q-toggle :icon="'app:tranq'" dense v-model="tranq" label="Enable Tranquil Air Totem Modifier?"></q-toggle>
                    </template>
                    <template v-slot:body-cell-name="player_class">
                        <q-td v-bind:class="{ background: props.row.faction }" :props="props">
                          <q-icon
                            :name="getIcon(props.row.player_class)"
                            size="20px"
                            :label="props.row.player_class"
                            class="q-ma-sm"
                            title=""
                          />
                          <span class="text-right">{{props.row.player_class}}</span>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-name="dps">
                        <q-td v-bind:class="{ background: props.row.dps }" :props="props">
                          <span class="text-right" v-if="!tranq">Rip at: {{props.row.dps}} DPS (very roughly estimated!)</span>
                          <span class="text-right" v-if="tranq">Rip at: {{(props.row.dps/.7).toPrecision(4)}} DPS (very roughly estimated!)</span>
                        </q-td>
                      </template>
                    </q-table>
                  </q-tab-panel>
                </q-tab-panels>
              </q-expansion-item>
            </q-item>
            <q-expansion-item flat default-closed class="bg-primary q-ma-lg row-auto" icon="help" label="Raw Data">
                <q-table
                  title=""
                  :pagination.sync="pagination"
                  dense
                  :data="getTableCols(value)"
                  :columns="columns"
                  row-key="name"
                  class="q-ma-md col"
                >
                  <template v-slot:top>
                    <q-btn flat dense justify-center icon="download" label="Download JSON" color="primary" @click="downloadJson(data)" class="q-mb-md" />
                  </template>
                </q-table>
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
    getThreatTableData(tps, faction) {
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
          if (faction === 'Horde') ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/classes[k].mod).toPrecision(4), faction: 'Horde', tranq: false });
          else if (faction === 'Alliance') ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod * .7)).toPrecision(4), faction: 'Alliance', tranq: false });
      });
      return ret;
    },
    downloadJson(filename, dl){
      const url = window.URL.createObjectURL(new Blob([dl]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${filename}.json`)
      document.body.appendChild(link)
      link.click()
    },
  },
  data () {
    return {
      name: 'RawResults',
      errorState: false,
      errorMsg: null,
      tab: 'Horde',
      tranq: false,
      pagination: {
        sortBy: 'field',
        rowsPerPage: [0,10],
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
        { name: 'player_class', align: 'center', label: 'Player Class', field: row => row.player_class, sortable: false },
        { name: 'dps', align: 'center', label: 'DPS to Rip Aggro', field: row => row.dps, sortable: false },
        { name: 'faction', label: 'Faction', field: row => row.faction, sortable: true },
        { name: 'tranq', label: 'Tranquil Air', field: row => row.tranq, sortable: false },
      ],
    }
  },
};
</script>
