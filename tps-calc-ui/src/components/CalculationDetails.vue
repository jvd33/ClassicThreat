<template>
  <q-page class="q-pa-md row">
    <q-table
      title="Threat Calculation Values"
      :data="data"
      separator="vertical"
      :columns="columns"
      row-key="name"
      dense
      dark
      color="amber"
      hide-bottom
      :pagination.sync="pagination"
      class="col"
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

  </q-page>
</template>

<style>
</style>

<script>
import axios from 'axios';


export default {
  methods: {
    getIcon(ability) {
      if (ability.includes('Defiance')) return 'app:defiance';
      if (ability.includes('Battle Shout')) return 'app:bs';
      if (ability.includes('Heroic Strike')) return 'app:hs';
      if (ability.includes('Revenge')) return 'app:revenge';

      switch(ability) {
        case 'Bloodthirst': return 'app:bt';
        case 'Shield Slam': return 'app:ss';
        case 'Defensive Stance': return 'app:dstance';
        case 'Sunder Armor': return 'app:sunder';
        case 'Rage Gain': return 'app:rage';
        case 'Thunder Clap': return 'app:tc';
        case 'Execute': return 'app:execute';
        case 'Gift Of Arthas': return 'app:goa';
        case 'Healing': return 'app:heals';
        case 'Tier1 Bonus': return 'app:t1';
        case 'Damage': return 'app:taunt';
        case 'Cleave': return 'app:cleave';
        case 'Demo Shout': return 'app:demo';
        case 'Battle Stance': return 'app:battle_stance';
        case 'Berserker Stance': return 'app:zerk_stance';
        case 'Shield Bash': return 'app:shield_bash';
        case 'Disarm': return 'app:disarm';
        case 'Hamstring': return 'app:hamstring';
        case 'Mocking Blow': return 'app:mb';
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
          name: 'val',
          align: 'center',
          label: 'Threat Value',
          field: 'val',
          format: val => `${val}`,
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
      ]
    ,
    data: [],
    }
  },
  mounted() {
    axios
    .get(process.env.VUE_APP_API_URL + '/api/v1/threat_values')
    .then(response => {
      this.data = response.data;
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
