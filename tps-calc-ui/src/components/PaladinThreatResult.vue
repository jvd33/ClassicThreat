<template>
  <q-page>
    <q-list bordered class="rounded-borders border-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :label="getRowTitle(name, value)" :caption="getCaption(name, value)">
        <q-card class="qa-pa-md">
          <q-card-section class="q-pa-sm row justify-around">
            <span class="text-h4 text-weight-bold text-center text-primary q-pa-md col-12 col-sm-12">
              Estimated TPS: {{value.tps.toPrecision(5)}}
              <br/>
              <br/>
            </span>
              <q-list dark bordered separator dense class="q-ma-sm col-auto">
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:rf" size="40px" class="q-mr-sm"/>Total Threat (estimated): <strong>{{value.total_threat_imp_rf.toPrecision(8)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:kings" size="40px" class="q-mr-sm"/>Greater Blessing Casts: <strong>{{value.greater_blessing_casts}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:kings" size="40px" class="q-mr-sm"/>Threat from Greater Blessings: <strong>{{(value.greater_blessing_hits * 60) * (1.6 + (value.imp_rf_pts/10)).toPrecision(6)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:righteousness" size="40px" class="q-mr-sm"/>Damage per Second: <strong>{{(value.total_damage/value.time).toPrecision(4)}}</strong></span>
                </q-item>
              </q-list>
              <dps-threat-result :results="value" :alliance-only="true"/>


            <q-expansion-item flat default-closed class="bg-primary q-ma-lg col-8 col-sm-8 justify-center" icon="help" label="Raw Data">
                <q-table
                  title=""
                  :pagination="pagination"
                  dense
                  :data="getTableCols(value)"
                  :columns="columns"
                  row-key="name"
                  class="q-ma-md"
                >
                  <template v-slot:top="props">
                    <q-btn flat dense justify-left icon="cloud_download" label="Download JSON" color="primary" @click="downloadJson(value.boss_name, value)" class="q-mb-sm" />
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
  name: 'PaladinThreatResult',
  props: ['results'],
  methods: {
    getIcon(ability) {
      if (ability.includes('ImpRf')) return 'app:imprf';
      switch(ability) {
        case 'Paladin': return 'app:paladin';
        case 'Swipe': return 'app:swipe';
        case 'Cower': return 'app:cower';
        case 'Faerie Fire': return 'app:ff';
        case 'Faerie Fire Feral': return 'app:ff';
        case 'Bear Form': return 'app:bear';
        case 'Demo Roar': return 'app:demoRoar';
        case 'Rage Gain': return 'app:rage';
        case 'Gift Of Arthas': return 'app:goa';
        case 'Healing': return 'app:heals';
        case 'Revenge': return 'app:revenge';
        case 'Warrior': return 'app:warr';
        case 'Mage': return 'app:mage';
        case 'Warlock (with imp)': return 'app:warlock';
        case 'Rogue': return 'app:rogue';
        case 'Druid': return 'app:druid';
        case 'Hunter': return 'app:hunter';
        default: return ability;
      };
    },
    getTableCols(data) {
      let ret = [];
      for (const prop in data) {
        if (prop !== 'gear' && prop !== 'dps_threat') {
          ret.push({'name': prop, 'value': data[prop]});
        }
      }
      return ret;
    },
    getRowTitle(name, val) {
      return `${name}: ${val.tps.toPrecision(5)} Estimated TPS`
    },
    getCaption(name, val) {
      if (!val.rank) {
        return 'Error loading rankings';
      }
      return `Rank: ${val.rank.toPrecision(3)}%`
    },
    downloadJson(filename, dl){
      const url = window.URL.createObjectURL(new Blob([JSON.stringify(dl, null, 2)]))
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
      pagination: {
        rowsPerPage: 0,
        sortBy: 'name',
      },
      columns: [
        { name: 'name', align: 'center', label: 'Metric', field: row => row.name, sortable: true },
        { name: 'value', align: 'center', label: 'Metric Value', field: row => row.value, sortable: true },
      ],
    }
  },
};
</script>
