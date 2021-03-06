<template>
  <q-page class="q-pa-md row-12" style="position: relative;" >
    <q-toolbar-title
      class="text-primary text-h3 text-weight-bold q-pb-lg col-auto col-sm shadow-2 wrap-auto text-h6-sm"
    >
      Druid Threat Estimator
    </q-toolbar-title>
    <q-form
      @submit="submit"
      class="q-gutter-md row-6 bordered rounded-borders"
      title="Druid Threat Estimator"
    >
      <q-input
        filled
        v-model="player_name"
        label="Character Name"
        lazy-rules
        title=""
        hint="As it appears in the provided log."
        dense
        :rules="[ val => val && val.length > 0 || 'Please type something']"
      >
      </q-input>

      <q-input
        filled
        v-model="url"
        label="Log URL"
        hint="A Classic Warcraft Logs 'https://classic.warcraftlogs.com/reports/<report_id>' URL"
        title=""
        lazy-rules
        dense
        :rules="[
          val => val && val.includes('classic.warcraftlogs.com/reports/')
          || 'Please enter a valid log URL.'
        ]"
      >
      </q-input>

      <q-select
        filled
        v-model="talent_pts"
        label="Points in Feral Instinct"
        :options="options"
        lazy-rules
        dense
        title=""
        :rules="[
          val => (!isNaN(val) && 0 <= val <= 5) || 'Invalid number of Feral Instinct points. 0 through 5, bro'
        ]"
      >
        <template v-slot:prepend>
          <q-icon name="app:fi" title="" />
        </template>
      </q-select>

      <q-select
        filled
        v-model="bosses"
        label="(Optional) Bosses"
        lazy-rules
        :options="boss_opts"
        :raids="raids"
        use-chips
        stack-label
        dense
        clickable
        multiple
        title=""
        clearable
        options-dense
        separator
        @clear="(value) => this.bosses = []"
      >
      </q-select>
      <q-toggle
        size="xl"
        class="col-2 col-sm-2 q-ma-sm q-pt-md"
        v-model="include_wipes"
        label="Calculate Threat on Wipes?"
        lazy-rules
        title=""
        dense
      />

      <div class="q-pt-lg q-mt-lg col-12 col-12-sm">
        <q-btn label="Estimate" type="submit" color="primary"/>
      </div>
      <div>
        <span class="row-1 text-weight-bold text-negative q-pt-md text-weight-bold text-h4"
           v-if="errorState"
        >
          {{errorMsg}}
        </span>
      </div>
    </q-form>
    <span class="h5 text-warning row">
            Percentile rankings are calculated only against logs that have been processed by ClassicThreat and are not entirely accurate (yet). <br/>
            Give more logs to make the percentiles more accurate!<br/>
            Wipes are not included in the pool of TPS values used for rank calculations.
          </span><br/>
          <span class="h6 text-accent">
            To contribute, report bugs, or propose features, see <router-link :to="'About'" class="text-accent text-weight-bold">about</router-link>
    </span>
    <threat-result class="q-mt-sm q-mb-sm" v-if="this.results" :results="this.results" player_class="Druid" />
    <q-expansion-item
      caption="Instructions"
      :default-opened="false"
      class="row-2 q-ma-lg justify-left bg-secondary shadow-4">
      <q-card>
        <q-card-section>
          Enter your character's name exactly as it appears on the logs.<br/>
          Provide a URL to your raid log. <br/>
          Full raid logs provided will be broken down per-encounter. <br/><br/>
          Note: For encounters with multiple enemies, the calculation does not differentiate between them (yet) so threat values are not representative of TPS for the actual named boss. <br/>
          Instead, it represents total TPS for <strong>every</strong> enemy fought during the same time window as the boss. Damage done to non-NPC targets (e.g., Mind Control) is not counted.
        </q-card-section>
      </q-card>
    </q-expansion-item>

  <q-inner-loading :showing="is_loading">
    <q-spinner-gears size="200px" />
    <span class="text-primary bg-secondary text-weight-bold q-pa-sm rounded-borders">
      Calculating...for full raid logs, this might take awhile.
    </span>
  </q-inner-loading>
  </q-page>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DruidCalculateForm',
  loading: true,
  data: () => {
      return {
          player_name: null,
          url: null,
          talent_pts: 5,
          friendlies_in_combat: 1,
          bosses: [],
          t1: false,
          include_wipes: true,
          options: [
              5, 4, 3, 2, 1, 0
          ],
          boss_opts: [
            'The Prophet Skeram', 'Silithid Royalty', 'Battleguard Sartura', 'Fankriss the Unyielding',
            'Princess Huhuran', 'Twin Emperors', 'Ouro', 'C\'Thun',

            'Kurinnaxx', 'General Rajaxx', 'Moam', 'Buru the Gorger', 'Ayamiss the Hunter', 'Ossirian the Unscarred',

            'High Priest Venoxis', 'High Priestess Jeklik', 'High Priestess Mar\'li',
            'Bloodlord Mandokir', 'Edge of Madness', 'High Priest Thekal', ' Gahz\'ranka',
            'High Priestess Arlokk', 'Jin\'do the Hexxer', 'Hakkar',

            'Razorgore the Untamed', 'Vaelastrasz the Corrupt', 'Broodlord Lashlayer',
            'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus', 'Nefarian',

            'Lucifron', 'Magmadar', 'Gehennas', 'Garr', 'Shazzrah',
            'Baron Geddon', 'Golemagg the Incinerator', 'Majordomo Executus',
            'Sulfuron Harbinger', 'Ragnaros',

            'Onyxia',
        ],
          raids: [
            {
              name: 'Molten Core',
              bosses: [
                'Lucifron', 'Magmadar', 'Gehennas', 'Garr',
                'Baron Geddon', 'Shazzrah', 'Sulfuron Harbinger', 'Golemagg the Incinerator',
                'Majordomo Executus', 'Ragnaros'
              ],
            },
            {
              name: 'Blackwing Lair',
              bosses: [
                'Razorgore the Untamed', 'Vaelastrasz the Corrupt',
                'Broodlord Lashlayer', 'Firemaw', 'Ebonroc', 'Flamegor', 'Chromaggus',
                'Nefarian'
              ],
            },
            {
              name: 'Onyxia\'s Lair',
              bosses: ['Onyxia'],
            },
          ],
          api_status: null,
          results: null,
          is_loading: false,
          errorState: false,
          errorMsg: null,
          route_guard: false,
          confirm: null,
      }
  },

  methods: {
    selected(value) {
      return this.bosses.includes(value);
    },
    submit() {
        this.errorState = false;
        this.errorMsg = null;
        this.results = null;
        this.is_loading = true;
        axios
        .post(process.env.VUE_APP_API_URL + '/api/v1/calculate_druid', {
          url: this.url,
          player_name: this.player_name,
          talent_pts: this.talent_pts,
          bosses: this.bosses || [],
          friendlies_in_combat: this.friendlies_in_combat,
          t1_set: this.t1,
          include_wipes: this.include_wipes,
        })
        .then(response => {
          this.api_status = response.status;
          this.results = response.data;
          this.is_loading = false;
        })
        .catch(error => {
            this.errorState = true;
            this.errorMsg = error.response && error.response.data && error.response.data.detail ?
              error.response.data.detail: 'Unexpected error. Try again later.';
        })
        .finally(() => this.is_loading = false);
    },
  },
  beforeRouteLeave(to, from, next) {
      if(this.is_loading) {
        this.$q.dialog({
          dark: true,
          title: 'Confirm',
          message: 'Are you sure you want to navigate away from this page?',
          cancel: true,
          persistent: true
        }).onOk(() => {
          next();
        });
      } else {
          next();
      }
  },
  meta() {
    return {
      title: 'Druid Threat Calculator',
      htmlAttr: {
        lang: 'en',
        amp: true
      },
      meta: {
        description: {name: 'description', content: 'Classic World of Warcraft Druid Threat Calculator'},
      },
    }
  },
};
</script>
