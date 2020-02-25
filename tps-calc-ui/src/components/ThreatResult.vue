<template>
  <q-page>
    <q-list bordered class="rounded-borders border-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :label="getRowTitle(name, value)"
        :caption="getCaption(name, value)"
        :icon="value.is_kill ? 'check_circle' : 'cancel'"
        :header-class="value.is_kill ? 'text-green' : 'text-red'">
        <q-card class="qa-pa-md">
          <q-card-section class="q-pa-sm row justify-center">
           <q-item tag="label" class="center col-12 shadow-8 q-ma-md">
              <q-item-section>
                <q-item-label class="text-h5">Active Time Only?</q-item-label>
                <q-item-label caption>Click here to only include active time in TPS calculations. Does not apply to rankings.</q-item-label>
              </q-item-section>
              <q-item-section avatar>
                <q-toggle color="primary" style="transform : scale(2.0, 2.0);" v-model="active_only"></q-toggle>
              </q-item-section>
            </q-item>
            <q-separator color="primary q-ma-sm" inset></q-separator>

            <span class="text-h4 text-weight-bold text-center text-primary q-pa-md col-12 col-sm-12">
              Total TPS: {{active_only ? ((value.modified_threat/value.active_time) || 0).toPrecision(5) : value.modified_tps.toPrecision(5)}}
              <br/>
              <span class="q-pa-md center text-subtitle2 justify-left text-white">
                <q-icon :name="tpsIcon(player_class)" size="40px" class="q-mr-sm"/>
                Total Threat:
                <strong>
                  {{value.modified_threat.toPrecision(8)}}
                </strong>
                <br/>
                <q-icon name="app:taunt" size="40px" class="q-mr-sm"/>
                Damage per Second:
                <strong>
                  {{active_only ? ((value.total_damage/value.active_time) ||0).toPrecision(4) : ((value.total_damage/value.time)||0).toPrecision(4)}}
                </strong>
                <br/>
                <br/>
                <q-icon name="help" size="20px" class="q-mr-sm">
                  <q-tooltip anchor="center left" self="center right" :offset="[10, 10]">
                      The percent of total encounter time spent with aggro on the boss.
                  </q-tooltip>
                </q-icon>
                Boss Tanking Time:
                <strong>
                  {{(value.time_with_aggro/value.time * 100).toPrecision(4)}}%
                </strong>
                <br/>
                <q-icon name="help" size="20px" class="q-mr-sm">
                  <q-tooltip anchor="center left" self="center right" :offset="[10, 10]">
                      Total threat per second of all events where you have aggro on the boss.
                  </q-tooltip>
                </q-icon>
                TPS With Boss Aggro:
                <strong>
                  {{value.time_with_aggro > 0 ? (value.threat_with_aggro/value.time_with_aggro).toPrecision(5) : 0}}
                </strong>
                <br/>
              </span>
            </span>
            <q-separator color="primary q-ma-sm" inset></q-separator>
            <threat-breakdown :events="value.events" :time="active_only ? value.active_time : value.time"/>
            <q-separator color="primary q-ma-md" inset></q-separator>
            <dps-threat-result :results="value" :ref_tps="active_only ? (value.modified_threat/value.active_time) : value.modified_tps"/>
            <q-btn dense justify-left icon="cloud_download" label="Download JSON" color="primary" @click="downloadJson(value.boss_name, value)" class="q-ma-md col-6 col-6-sm shadow-10"/>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </q-list>
  </q-page>
</template>
<script>
export default {
  name: 'ThreatResult',
  props: ['results', 'player_class'],
  player_class: '',
  methods: {
    getRowTitle(name, val) {
      return `${name}: ${val.modified_tps.toPrecision(5)} Estimated TPS`
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
    tpsIcon(pl_class) {
      switch(pl_class) {
        case 'Warrior': return 'app:dstance';
        case 'Druid': return 'app:bear';
        case 'Paladin': return 'app:rf';
        default: return 'app:defaultability';
      }
    },
  },
  data () {
    return {
      name: 'RawResults',
      errorState: false,
      errorMsg: null,
      active_only: false,
      pagination: {
        rowsPerPage: 0,
      },
      columns: [
        { name: 'name', align: 'center', label: 'Metric', field: row => row.name, sortable: true },
        { name: 'value', align: 'center', label: 'Metric Value', field: row => row.value, sortable: true },
      ],
    }
  },
};
</script>
