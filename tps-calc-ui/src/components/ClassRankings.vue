<template>
  <q-page class="q-pa-md">
    <q-tabs
      v-model="boss"
      dense
      align="justify"
      no-caps
      class="text-white shadow-2 rounded-borders"
      active-bg-color="primary"
    >
      <q-btn-dropdown auto-close stretch flat label="Bosses..">
        <q-list highlight separator>
          <q-item v-for="(boss, index) in bosses" highlight separator  @click="this.boss = boss" :label="boss" />
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </q-tabs>
    <q-tab-panel name="rankings" icon="app:warr">
      <q-table
        title="`${this.class} Threat Rankings: ${this.boss}`"
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
        no-data-label="Failed to load threat rankings. Please try again later or file a bug report if it persists."
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
    </q-tab-panels>
  </q-page>
</template>

<style>
</style>

<script>
import axios from 'axios';


export default {
  methods: {

  },
  data () {
    return {
      name: 'ClassRankings',
      loading: true,
      class: null,
      errorState: false,
      tab: 'warrior',
      boss: 'Lucifron',
      bosses: [
        'Lucifron', 'Magmadar', 'Gehennas', 'Garr',
        'Baron Geddon', 'Shazzrah', 'Sulfuron Harbinger', 'Golemagg the Incinerator',
        'Majordomo Executus', 'Ragnaros', 'Razorgore the Untamed', 'Vaelastrasz the Corrupt',
        'Broodlord Lashlayer', 'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus',
        'Nefarian', 'Onyxia'
      ],
      errorMsg: null,
      boss_pagination: {
        rowsPerPage: [10, 20, 50],
        sortBy: 'tps',
        descending: true
      }
      columns: [
        {
          name: 'name',
          required: true,
          label: 'Player',
          align: 'left',
          field: row => `${row.name} - ${row.realm}`,
          sortable: true
        },
        {
          name: 'realm',
          required: true,
          label: 'Realm',
          align: 'left',
          field: 'realm',
        }
        {
          name: 'tps',
          align: 'center',
          label: 'Threat per Second (TPS)',
          field: 'tps',
          format: val => `${val.toPrecision(5)}`,
          sortable: true
        },
        {
          name: 'report',
          align: 'center',
          label: 'Threat Calculation Type',
          field: 'report',
          format: val => `${val}`,
          sortable: true
        },
        {
          name: 'total_threat',
          align: 'center',
          label: 'Total Threat,
          field: 'total_threat',
          format: val => `${val}`,
          sortable: true
        },
      ],
    }
  },
  mounted() {
    axios
    .get(process.env.VUE_APP_API_URL + '/api/v1/threat_values?player_class=Warrior')
    .then(response => {
      this.warr_data = response.data;
      this.loading = false;
    })
    .catch(error => {
        this.errorState = true;
        this.errorMsg = error.response ?
          error.response.data.details : 'Unexpected error. Try again later.';
    })

    axios
    .get(process.env.VUE_APP_API_URL + '/api/v1/threat_values?player_class=Druid')
    .then(response => {
      this.druid_data = response.data;
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
