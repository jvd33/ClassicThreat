<template>
  <q-page>
    <q-list bordered class="rounded-borders" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name" class="q-pa-sm">
        <q-card>
          <q-card-section>
            <span class="text-h5 text-center">
              Raw Estimated Threat Per Second: <strong class="text-h4 text-primary">{{value.tps.toPrecision(5)}}</strong>
              <br/>
              <br/>
            </span>
             
            <q-expansion-item popup default-closed icon="help" label="Raw Data">
              <div class="q-pa-md">
                <q-table
                  title=""
                  dense
                  :data="getTableCols(value)"
                  :columns="columns"
                  row-key="name"
                />
              </div>  
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
        default: return ability;
      };
    },
    getTableCols(data) {
      ret = []
      for (const prop in data) { 
        ret.push({'name': prop, 'value': data[prop]})
      }
      return ret; 
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
      columns: {
        { name: 'Metric', align: 'center', label: 'Metric', field: 'name', sortable: true },
        { name: 'Metric Value', align: 'center', label: 'Metric Value', field: 'value', sortable: true },
      },
    }
  },
};
</script>
