<template>
  <q-page class="q-pa-md">
   <q-tabs
    v-model="tab"
    dense
    align="justify"
    no-caps
    class="text-white shadow-2 rounded-borders"
    active-bg-color="primary"
  >
    <q-tab name="warrior" icon="app:warr" label="Warrior" />
    <q-tab name="druid" icon="app:druid" label="Druid" />
    <q-tab name="paladin" icon="app:paladin" label="Paladin" />
  </q-tabs>
  <q-tab-panels v-model="tab" animated class="shadow-2 rounded-borders row" transition-prev="fade" transition-next="fade">
    <q-tab-panel name="warrior" icon="app:warr">
      <q-table
        title="Warrior Threat Calculation Values"
        :data="warr_data"
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
    </q-tab-panel>
    <q-tab-panel name="druid" icon="app:druid">
      <q-table
        title="Druid Threat Calculation Values"
        :data="druid_data"
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
    </q-tab-panel>
    <q-tab-panel name="paladin" icon="app:paladin">
      <q-table
        title="Paladin Threat Calculation Values"
        :data="paladin_data"
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
    </q-tab-panel>
</q-tab-panels>

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
      if (ability.includes('Feral Instinct')) return 'app:fi';
      if (ability.includes('Battle Shout')) return 'app:bs';
      if (ability.includes('Heroic Strike')) return 'app:hs';
      if (ability.includes('Revenge')) return 'app:revenge';
      if (ability.includes('Holy Shield')) return 'app:holyshield';
      if (ability.includes('Blessing Of Might')) return 'app:might';
      if (ability.includes('Blessing Of Sacrifice')) return 'app:sac';
      if (ability.includes('Blessing Of Kings')) return 'app:kings';
      if (ability.includes('Blessing Of Sanctuary')) return 'app:sanctuary';
      if (ability.includes('Blessing Of Protection')) return 'app:bop';
      if (ability.includes('Blessing Of Light')) return 'app:light';
      if (ability.includes('Blessing Of Salvation')) return 'app:salv';
      if (ability.includes('Imp Rf')) return 'app:rf';


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
        case 'Maul': return 'app:maul';
        case 'Swipe': return 'app:swipe';
        case 'Cower': return 'app:cower';
        case 'Faerie Fire': return 'app:ff';
        case 'Faerie Fire Feral': return 'app:ff';
        case 'Bear Form': return 'app:bear';
        case 'Cat Form': return 'app:cat';
        case 'Demo Roar': return 'app:demoRoar';
        case 'Cleanse': return 'app:cleanse';
        case 'Righteous Fury': return 'app:rf';
        case 'Blessing Of Freedom': return 'app:freedom';
        case 'Paladin Spell Healing': return 'app:holylight';
        case 'Mana Gain': return 'app:manapot';
        default: return ability;
      };
    },
  },
  metaInfo: {
    title: 'Threat Values',
    htmlAttrs: {
      lang: 'en',
      amp: true
    }
  },
  data () {
    return {
      name: 'CalculationDetails',
      loading: true,
      errorState: false,
      tab: 'warrior',
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
    warr_data: [],
    druid_data: [],
    paladin_data: [],
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

    axios
    .get(process.env.VUE_APP_API_URL + '/api/v1/threat_values?player_class=Paladin')
    .then(response => {
      this.paladin_data = response.data;
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
