<template>
  <q-page class="q-pa-md">
    <q-item>
      <span class="text-primary text-h4 col-12 col-12-sm" >{{ getTitle() }}</span>
    </q-item>
    <q-table
      :title="getTitle()"
      :data="getData()"
      :v-model="player_class"
      separator="horizontal"
      :columns="columns"
      row-key="`${name}:${rank}:${report}"
      dark
      color="amber"
      :pagination.sync="boss_pagination"
      no-data-label="Failed to load threat rankings. Please try again later or file a bug report if it persists."
    >
      <template v-slot:top>
          <q-item-section>
            <q-select
              v-model="boss"
              label="Bosses"
              lazy-rules
              :options="bosses"
              stack-label
              dense
              outlined
              separator
              highlight
              class="border-primary col-5-sm col-5"
              dark
              @input = "selected(boss)"
              :filterMethod="filterTable(filter)"
            >

            </q-select>
            <q-space/>
            <q-separator vertical inset class="bg-primary q-ma-lg" ></q-separator>
            <q-input dense debounce="500" color="primary" v-model="filter" label="Search..." class="col-5 col-5-sm" highlight>
              <template v-slot:append>
                <q-icon name="search" ></q-icon>
              </template>
            </q-input>
            <q-space/>
            <q-separator vertical inset class="bg-primary q-ma-lg" ></q-separator>
            <q-toggle class="text-primary col-2 col-2-sm" label="Best Parses Only?" dense dark elevated highlight justify-right v-model="best_ranks">

            </q-toggle>
          </q-item-section>
      </template>
      <template v-slot:body-cell-rank="props">
        <q-item justify-left separator highlight>
          <q-item-section justify-left class="q-tr">
            <q-btn type="a" :href="getHref(props.row)" name="link" style="width:100%" icon="link" :label="props.row.rank"></q-btn>
          </q-item-section>
        </q-item>
      </template>
    </q-table>
    <q-inner-loading :showing="loading">
      <q-spinner-puff size="250px" class="q-mb-sm" color="primary"/>
      <span class="text-primary bg-secondary text-weight-bold q-pa-sm rounded-borders">
        Fetching Rankings...
      </span>
    </q-inner-loading>
    <span class="text-primary text-h6 col-12 col-12-sm">Rankings update once every minute!</span>
  </q-page>
</template>

<style>
</style>

<script>
import axios from 'axios';


export default {
  props: {
    player_class: null,
  },
  methods: {
    getHref(row) {
      return `https://classic.warcraftlogs.com/reports/${row.report}#fight=${row.boss_id}`
    },
    getTitle() {
      return `${this.player_class} Rankings - ${this.boss}`
    },
    getData() {
      if (this.boss_cache[this.player_class][this.boss] !== undefined) {
        this.loading = false;
        return this.filterTable(this.filter);
      }
      axios
      .get(process.env.VUE_APP_API_URL + `/api/v1/rankings?player_class=${this.player_class}&boss=${this.boss}`)
      .then(response => {
        this.data = response.data;
        this.boss_cache[this.player_class][this.boss] = response.data
        this.loading = false;
      })
      .catch(error => {
          this.errorState = true;
          this.loading = false;
          this.errorMsg = error.response ?
            error.response.data.details : 'Unexpected error. Try again later.';
          this.data = [];
      })
      return this.data;
    },
    selected(val) {
      this.boss = val;
      this.loading = true;
      if (this.boss_cache[this.player_class][val] !== undefined) {
        this.data = this.boss_cache[this.player_class][val];
        this.loading = false;
        return;
      }
      this.getData();
      return this.filterTable(this.filter);
    },
    filterTable(filter) {
      if (this.boss_cache[this.player_class][this.boss] === undefined) {
        return this.data;
      }
      let d = this.boss_cache[this.player_class][this.boss].filter((val) => val.player.includes(filter) || val.realm.includes(filter))
      let seen = []
      let final = []
      if (this.best_ranks === true) {
        d.forEach((x) => {
          if (!seen.includes(x.player)) {
            final.push(x);
            seen.push(x.player);
          }
        });
        d = final;
      }
      this.data = d;
      return d;
    },
  },
  data () {
    return {
      filter: '',
      best_ranks: false,
      name: 'ClassRankings',
      loading: true,
      errorState: false,
      boss: 'Lucifron',
      data: [],
      boss_cache: {
        'Warrior': {},
        'Druid': {}
      },
      bosses: [
        'Lucifron', 'Magmadar', 'Gehennas', 'Garr',
        'Baron Geddon', 'Shazzrah', 'Sulfuron Harbinger', 'Golemagg the Incinerator',
        'Majordomo Executus', 'Ragnaros', 'Razorgore the Untamed', 'Vaelastrasz the Corrupt',
        'Broodlord Lashlayer', 'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus',
        'Nefarian', 'Onyxia'
      ],
      errorMsg: null,
      boss_pagination: {
        rowsPerPage: 25,
        recordsPerPage: [0, 10, 25, 50],
        sortBy: 'rank',
        descending: false,
      },
      columns: [
        {
          name: 'rank',
          required: true,
          label: 'Rank',
          align: 'left',
          field: row => row.rank,
          headerClasses: 'bg-primary',
          style: 'font-weight: 750;max-width:20px;'
        },
        {
          name: 'player',
          required: true,
          label: 'Player',
          align: 'left',
          field: row => `${row.player} - ${row.realm}`,
          classes: 'ellipsis',
          style: 'max-width: 100px',
          headerClasses: 'bg-primary',
          style: 'font-weight: 750'
        },
        {
          name: 'tps',
          align: 'left',
          label: 'Threat per Second (TPS)',
          field: 'tps',
          format: val => `${val.toPrecision(6)}`,
          headerClasses: 'bg-primary',
        },
        {
          name: 'total_threat',
          align: 'left',
          label: 'Total Threat',
          field: 'total_threat',
          format: val => `${parseFloat(val).toPrecision(7)}`,
          headerClasses: 'bg-primary'
        },
      ],
    }
  },
  mounted() {
    this.loading = true;
    axios
      .get(process.env.VUE_APP_API_URL + `/api/v1/rankings?player_class=${this.player_class}&boss=${this.boss}`)
      .then(response => {
        this.data = response.data;
        this.boss_cache[this.player_class][this.boss] = response.data
        this.loading = false;
      })
      .catch(error => {
          this.errorState = true;
          this.errorMsg = error.response ?
            error.response.data.details : 'Unexpected error. Try again later.';

          this.data = [];
      })
  },
};
</script>
