<template>
  <div class="q-pa-md">
    <q-table
      title="Threat Calculation Values"
      :data="data"
      separator="vertical"
      :columns="columns"
      row-key="name"
      dark
      color="amber"
      :pagination.sync="pagination"
      no-data-label="Failed to load threat values. Please try again later or file a bug report if it persists."
    >
      <template v-slot:body-cell-name="props" >
        <q-td>
          <q-icon
            :name="getIcon(props.value)"
            size="32px"
            :label="props.value"
	          class="q-ma-sm"
            title=""
          />
	        <span class="text-right sortable">{{props.value}}</span>
        </q-td>
      </template>

    </q-table>

  </div>
</template>

<style>
</style>

<script>
import axios from 'axios';


export default {
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
        case 'Damage': return 'app:taunt';
        case 'Cleave': return 'app:cleave';
        default: return ability;
      };
    },
  },
  data () {
    return {
      name: 'CalculationDetails',
      loading: true,
      errorState: false,
      errorMsg: null,
      pagination: {
        rowsPerPage: 0,
        sortBy: 'val',
        descending: true
      },
      columns: [
        {
          name: 'name',
          required: true,
          label: 'Ability',
          align: 'left',
          field: row => row.name,
          format: val => `${val.replace(/([A-Z])/g, ' $1').trim()}`,
          sortable: true
        },
        {
          name: 'threat_type',
          align: 'center',
          label: 'Threat Calculation Type',
          field: 'threat_type',
          format: val => `${val}`,
          sortable: true
        },
        {
          name: 'val',
          align: 'center',
          label: 'Threat Value',
          field: 'val',
          format: val => `${val}`,
          sortable: true
        },
      ]
    ,
    data: [],
    }
  },
  mounted() {
    axios
    .get(process.env.VUE_APP_API_URL + '/v1/api/threat_values')
    .then(response => {
      this.data = JSON.parse(response.data);
      this.loading = false;
    })
    .catch(error => {
        this.errorState = true;
        this.errorMsg = error.response ?
          error.response.data.details : 'Unexpected error. Try again later.';
    })
    .finally(() => this.is_loading = false);
  },
};
</script>
