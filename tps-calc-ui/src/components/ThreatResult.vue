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
            <q-list elevated dark bordered separator>
              <q-item v-if="value.bt_count > 0" class="q-pa-md">
                <q-item-section class="row"><span class="col-8"><q-icon name="app:bt" class="col-3 q-mr-sm" size="40px"/>
                Bloodthirst Casts Per Minute: {{(value.bt_count/(value.time/60)).toPrecision(4)}}</span>
                </q-item-section>
			        </q-item>
            <q-item v-if="value.shield_slam_count > 0" class="q-pa-md" >
              <q-item-section class="row">
				        <span class="col-8">
                  <q-icon name="app:ss" size="40px" class="col-3 q-mr-sm"/>
                    Shield Slam Casts Per Minute: {{(value.shield_slam_count/(value.time/60)).toPrecision(4)}}</span>
              </q-item-section>
            </q-item>
            <q-item class="q-pa-md" >
              <q-item-section class="row"><span class="col-8"><q-icon name="app:revenge" size="40px" class="col-3 q-mr-sm"/>Revenge Casts Per Minute: {{(value.revenge_count/(value.time/60)).toPrecision(4)}}</span></q-item-section>
            </q-item>
            <q-item class="q-pa-md" >
              <q-item-section class="row"><span class="col-8"><q-icon name="app:sunder" class="col=3 q-mr-sm" size="40px"/>Sunder Armor Hits Per Minute: {{(value.sunder_count/(value.time/60)).toPrecision(4)}}</span></q-item-section>
            </q-item>
            <q-item class="q-pa-md" >
              <q-item-section class="row"><span class="col-8"><q-icon name="app:hs" size="40px" class="col-3 q-mr-sm"/>Heroic Strike Casts Per Minute: {{(value.hs_count/(value.time/60)).toPrecision(4)}}</span></q-item-section>
            </q-item>
            </q-list>
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
      columns: [
        { name: 'Metric', align: 'center', label: 'Metric', field: 'name', sortable: true },
        { name: 'Metric Value', align: 'center', label: 'Metric Value', field: 'value', sortable: true },
      ],
    }
  },
};
</script>
