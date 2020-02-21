<template>
<q-page class="q-pa-sm col-12 col-sm-12 text-center" style="min-height: inherit">
  <span class="text-h5 text-white col-12 col-sm-12">
    Estimated DPS Caps
  </span>
  <q-tabs
    v-model="tab"
    dense
    align="justify"
    no-caps
    class="text-white shadow-2 rounded-borders q-pt-md"
  >
    <q-tab v-if="this.results.player_class !== 'Paladin'" name="horde" icon="app:horde" label="Horde" style="background: #5f110d"/>
    <q-tab name="alliance" icon="app:alliance" label="Alliance" style="background: #1b3658"/>
  </q-tabs>
  <q-tab-panels v-model="tab" animated class="shadow-2 rounded-borders row" transition-prev="fade" transition-next="fade">
    <q-tab-panel name="alliance" icon="app:alliance" style="background: #1b3658">
      <q-table
        title=""
        label="alliance"
        hide-header
        :pagination="pagination"
        :columns="threatCols"
        :data="getThreatTableData(ref_tps, 'Alliance')"
        row-key="name"
        hide-bottom
        class="wrap"
      >
        <template v-slot:body-cell-class="props" class="justify-around">
          <q-td :props="props">
            <q-icon
              :name="getIcon(props.row.class)"
              size="20px"
              :label="props.row.class"
              class="q-ma-sm"
              title=""
            />
            <span>{{props.row.class}}</span>
          </q-td>
        </template>
        <template v-slot:body-cell-dps="props">
          <q-td :props="props">
            <span>Rips at: <span class="text-primary text-h6 text-weight-bold">{{props.row.dps}} DPS</span> (roughly)</span>
          </q-td>
        </template>
      </q-table>
    </q-tab-panel>
    <q-tab-panel name="horde" icon="app:horde" value="horde" style="background: #5f110d" v-if="this.results.player_class !== 'Paladin'">
      <q-table
        title=""
        label="horde"
        :columns="threatCols"
        :pagination="pagination"
        :data="getThreatTableData(ref_tps, 'Horde')"
        row-key="name"
        hide-header
        class="wrap"
      >
      <template v-slot:body-cell-class="props">
          <q-td :props="props">
            <q-icon
              :name="getIcon(props.row.class)"
              size="20px"
              :label="props.row.class"
              class="q-ma-sm"
              title=""
            />
            <span>{{props.row.class}}</span>
          </q-td>
        </template>
        <template v-slot:body-cell-dps="props">
          <q-td :props="props">
            <span v-if="!tranq">Rips at:  <span class="text-primary text-h6 text-weight-bold">{{props.row.dps.toPrecision(4)}} DPS</span>  (roughly)</span>
            <span v-if="tranq">Rips at: <span class="text-primary text-h6 text-weight-bold">{{(props.row.dps/.7).toPrecision(4)}} DPS</span> (roughly)</span>
          </q-td>
        </template>
        <template v-slot:bottom="props">
          <q-toggle :icon="'app:tranq'" dense v-model="tranq" label="Enable Tranquil Air Totem Modifier?"></q-toggle>
        </template>
      </q-table>
    </q-tab-panel>
  </q-tab-panels>
  </q-page>
</template>

<style>
</style>

<script>
export default {
name: 'DPSThreat',
  props: ['results', 'allianceOnly', 'ref_tps'],
  methods: {
    getIcon(cls) {
      switch(cls) {
        case 'Warrior': return 'app:warr';
        case 'Mage': return 'app:mage';
        case 'Warlock (with imp)': return 'app:warlock';
        case 'Rogue': return 'app:rogue';
        case 'Druid': return 'app:druid';
        case 'Ranged (no reduction)': return 'app:hunter';
        default: return 'app:warr';
      };
    },

    getThreatTableData(tps, faction) {
      let top_fury = this.results ?
        this.results.dps_threat.reduce((max, player) => max.total_dmg > player.total_dmg ? max : player) :
        {
          player_name: 'Warrior',
          hs_cpm: 20,
          execute_percent: .2,
        };

      let name = top_fury.player_name || 'Warrior';
      let classes = {
        'Mage': {mod: () => .7, rip_at: 1.3},
        'Warlock (with imp)': {mod: () => .8, rip_at: 1.3},
        'Rogue': {mod: () => .71, rip_at: 1.1},
        'Druid': {mod: () => .71, rip_at: 1.1},
        'Ranged (no reduction)': {mod: () => 1, rip_at: 1.3},
      };

      classes[name] = {
          mod: () => {
            return tps/((((tps - ((top_fury.hs_cpm/60) * 145 * .8)) * 1.1/.8) * (1 - (top_fury.execute_percent/100)))
            + ((top_fury.execute_percent/100) * (tps + ((top_fury.hs_cpm/60) * 145 * .8) * 1.1))) // quick maths
          },
          rip_at: 1
      };

      let ret = [];
      Object.keys(classes).forEach((k) => {
          if (faction === 'Horde') ret.push({class: k, dps: (tps*classes[k].rip_at)/classes[k].mod().toPrecision(4), faction: 'Horde', tranq: false });
          else if (faction === 'Alliance') ret.push({class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod() * .7)).toPrecision(4), faction: 'Alliance', tranq: false });
      });
      return ret.sort((a, b) => {return a.dps - b.dps});
    },
  },
  data () {
    return {
      name: 'DPSThreat',
      errorState: false,
      errorMsg: null,
      tab: this.results.player_class === 'Paladin' ? 'alliance' : 'horde',
      tranq: false,
      pagination: {
        rowsPerPage: 0,
      },
      threatCols:  [
        { name: 'class', align: 'center', label: 'Player Class', field: row => row.class, sortable: false },
        { name: 'dps', align: 'center', label: 'DPS to Rip Aggro', field: row => row.dps, sortable: true },
      ],
    }
  },
};
</script>
