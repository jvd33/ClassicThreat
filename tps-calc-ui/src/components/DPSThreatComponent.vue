<template>
<q-page>
    <q-header>Hi</q-header>
    <q-tabs
      v-model="tab"
      dense
      align="justify"
      no-caps
      class="text-white shadow-2 rounded-borders"
    >
      <q-tab name="horde" icon="app:horde" label="Horde" style="background: #5f110d"/>
      <q-tab name="alliance" icon="app:alliance" label="Alliance" style="background: #1b3658"/>
    </q-tabs>
    <q-tab-panels v-model="tab" animated class="shadow-2 rounded-borders row" transition-prev="fade" transition-next="fade">
      <q-tab-panel name="alliance" icon="app:alliance" style="background: #1b3658" class="col-6 col-sm-6 fit">
        <q-table
          title=""
          label="alliance"
          hide-header
          :columns="threatCols"
          :visible-columns="['class', 'dps']"
          :data="getThreatTableData(results.tps, 'Alliance')"
          row-key="name"
          hide-bottom
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
              <span class="text-right">{{props.row.class}}</span>
            </q-td>
          </template>
          <template v-slot:body-cell-dps="props">
            <q-td :props="props">
              <span class="text-right">Rips at: <span class="text-primary text-h6 text-weight-bold">{{props.row.dps}} DPS</span> (roughly)</span>
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>
      <q-tab-panel name="horde" icon="app:horde" value="horde" style="background: #5f110d">
        <q-table
          title=""
          label="horde"
          :columns="threatCols"
          :visible-columns="['class', 'dps']"
          :data="getThreatTableData(results.tps, 'Horde')"
          row-key="name"
          hide-header
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
              <span class="text-right">{{props.row.class}}</span>
            </q-td>
          </template>
          <template v-slot:body-cell-dps="props">
            <q-td :props="props">
              <span class="text-right" v-if="!tranq">Rips at:  <span class="text-primary text-h6 text-weight-bold">{{props.row.dps}} DPS</span>  (very roughly estimated!)</span>
              <span class="text-right" v-if="tranq">Rips at: <span class="text-primary text-h6 text-weight-bold">{{(props.row.dps/.7).toPrecision(4)}} DPS</span> (very roughly estimated!)</span>
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
  props: ['results'],
  methods: {
    getIcon(cls) {
      switch(cls) {
        case 'Warrior': return 'app:warr';
        case 'Mage': return 'app:mage';
        case 'Warlock (with imp)': return 'app:warlock';
        case 'Rogue': return 'app:rogue';
        case 'Druid': return 'app:druid';
        case 'Hunter': return 'app:hunter';
        default: return cls;
      };
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
          if (faction === 'Horde') ret.push({class: k, dps: ((tps*classes[k].rip_at)/classes[k].mod).toPrecision(4), faction: 'Horde', tranq: false });
          else if (faction === 'Alliance') ret.push({class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod * .7)).toPrecision(4), faction: 'Alliance', tranq: false });
      });
      return ret.sort((a, b) => {return a.dps - b.dps});
    },
  },
  data () {
    return {
      name: 'DPSThreat',
      errorState: false,
      errorMsg: null,
      tab: 'horde',
      tranq: false,
      threatCols:  [
        { name: 'class', align: 'center', label: 'Player Class', field: row => row.class, sortable: false },
        { name: 'dps', align: 'center', label: 'DPS to Rip Aggro', field: row => row.dps, sortable: true },
        { name: 'faction', label: 'Faction', field: row => row.faction, sortable: false },
        { name: 'tranq', label: 'Tranquil Air', field: row => row.tranq, sortable: false },
      ],
    }
  },
};
</script>
