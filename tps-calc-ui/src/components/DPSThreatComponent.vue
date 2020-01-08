<template>
<q-page>
  <q-expansion-item
      default-opened
      flat header-class="bg-primary"
      class="q-ma-md"
      label="DPS Rip Thresholds"
      icon="warning"
      expand-icon-class=""
    >
      <q-tabs
        :v-model="tab"
        dense
        align="justify"
      >
        <q-tab name="Horde" icon="app:horde" label="Horde"/>
        <q-tab name="Alliance" icon="app:alliance" label="Alliance"/>
      </q-tabs>
      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="Alliance">
          <q-table
            title=""
            :label="Alliance"
            class="q-ma-md bg-alliance"
            :pagination.sync="threat_pagination"
            hide-header
            :columns="threatCols"
            visible-columns="['player_class', 'dps']"
            :data="getThreatTableData(tank_tps, 'Alliance')"
            row-key="name"
            hide-bottom
          >
            <template v-slot:body-cell-name="player_class">
              <q-td :props="props">
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
            :columns="threatCols"
            visible-columns="['player_class', 'dps']"
            :data="getThreatTableData(tank_tps, 'Horde')"
            row-key="name"
            hide-header
            hide-bottom
          >
          <template v-slot:top="props">
            <q-toggle :icon="'app:tranq'" dense v-model="tranq" label="Enable Tranquil Air Totem Modifier?"></q-toggle>
          </template>
          <template v-slot:body-cell-name="player_class">
              <q-td :props="props">
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
              <q-td :props="props">
                <span class="text-right" v-if="!tranq">Rip at: {{props.row.dps}} DPS (very roughly estimated!)</span>
                <span class="text-right" v-if="tranq">Rip at: {{(props.row.dps/.7).toPrecision(4)}} DPS (very roughly estimated!)</span>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-expansion-item>
  </q-page>
</template>

<style>
</style>

<script>
export default {
name: 'DPSThreat',
  props: ['tank_tps'],
  tab: 'Horde',
  tranq: false,
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
          if (faction === 'Horde') ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/classes[k].mod).toPrecision(4), faction: 'Horde', tranq: false });
          else if (faction === 'Alliance') ret.push({player_class: k, dps: ((tps*classes[k].rip_at)/(classes[k].mod * .7)).toPrecision(4), faction: 'Alliance', tranq: false });
      });
      return ret;
    },
  },
  data () {
    return {
      name: 'DPSThreat',
      errorState: false,
      errorMsg: null,
      threat_pagination: {
        sortBy: 'faction',
        descending: false,
        rowsPerPage: 0,
      },
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
