<template>
  <div class="q-pa-md">
    <span class="row-1 text-weight-bold text-negative q-pt-md text-weight-bold bg-secondary relative-position"
       v-if="this.errorState"
    >
      {{this.errorMsg}}
    </span>
    <q-table
      title="Threat Calculation Values"
      :data="data"
      :columns="columns"
      row-key="name"
      dark
      color="amber"
    />
    <q-inner-loading v-if="is_loading || errorState">
      <q-spinner-gears size="200px" v-if="is_loading" />
      <span class="text-primary bg-secondary text-weight-bold q-pa-sm rounded-borders" v-else-if="errorState">
        <q-icon name="error" class="justify-left" />
        {{ this.errorMsg }}
      </span>
    </q-inner-loading>
  </div>
</template>

<style>
</style>

<script>
import axios from 'axios';

export default {
  data () {
    return {
      name: 'CalculationDetails',
      is_loading: true,
      errorState: false,
      errorMsg: null,
      columns: [
        {
          name: 'ability',
          required: true,
          label: 'Ability',
          align: 'left',
          field: row => row.type,
          format: val => `${val}`,
          sortable: true
        },
        {
          name: 'type',
          align: 'center',
          label: 'Threat Calculation Type',
          field: 'threat_type',
          format: val => `${val.threat_type}`,
          sortable: true
        },
        {
          name: 'threat',
          align: 'center',
          label: 'Threat Value',
          field: 'val',
          format: val => `${val.val}`,
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
      this.is_loading = false;
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
