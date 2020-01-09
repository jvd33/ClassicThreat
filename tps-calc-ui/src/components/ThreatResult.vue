<template>
  <q-page>
    <q-list bordered class="rounded-borders border-primary q-mb-lg" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name">
        <q-card class="qa-pa-md">
          <q-card-section class="q-pa-sm row justify-around">
            <span class="text-h4 text-weight-bold text-center text-primary q-pa-md col-12 col-sm-12">
              Estimated TPS: {{value.tps.toPrecision(5)}}
              <br/>
              <br/>
            </span>
              <q-list dark bordered separator dense class="q-ma-sm col-auto">
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:dstance" size="40px" class="q-mr-sm"/>Total Threat (estimated): <strong>{{value.total_threat_defiance.toPrecision(8)}}</strong></span>
                </q-item>
                <q-item v-if="value.bt_count > 0" class="q-pa-md">
                <span class="q-pa-md"><q-icon name="app:bt" class="q-mr-sm" size="40px"/>
                  Bloodthirst Casts Per Minute: <strong>{{(value.bt_count/(value.time/60)).toPrecision(4)}}</strong></span>
                </q-item>
                <q-item v-else-if="value.shield_slam_count > 0" class="q-pa-md" >
                    <span class="q-pa-md">
                      <q-icon name="app:ss" size="40px" class="q-mr-sm"/>
                        Shield Slam Casts Per Minute: <strong>{{(value.shield_slam_count/(value.time/60)).toPrecision(4)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                <span class="q-pa-md"><q-icon name="app:revenge" size="40px" class="q-mr-sm"/>
                  Revenge Casts Per Minute: <strong>{{(value.revenge_count/(value.time/60)).toPrecision(4)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:sunder" class="q-mr-sm" size="40px"/>Sunder Armor Hits Per Minute: <strong>{{(value.sunder_count/(value.time/60)).toPrecision(4)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:hs" size="40px" class="q-mr-sm"/>Heroic Strike Casts Per Minute: <strong>{{(value.hs_count/(value.time/60)).toPrecision(4)}}</strong></span>
                </q-item>
                <q-item class="q-pa-md" >
                  <span class="q-pa-md"><q-icon name="app:taunt" size="40px" class="q-mr-sm"/>Damage per Second: <strong>{{(value.total_damage/value.time).toPrecision(4)}}</strong></span>
                </q-item>
              </q-list>
              <dps-threat-result :results="value" />


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
