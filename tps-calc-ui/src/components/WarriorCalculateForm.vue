<template>
  <q-page class="q-pa-md row-12" style="position: relative;" >
    <q-toolbar-title
      class="text-primary text-h3 justify-center text-weight-bold q-pb-lg"
    >
      Warrior Threat Estimator
    </q-toolbar-title>

    <q-form
      @submit="submit"
      class="q-gutter-md row-6 bordered rounded-borders"
      title="Warrior Threat Estimator"
    >
      <q-input
        filled
        v-model="player_name"
        label="Character Name"
        lazy-rules
        title=""
        dense
        :rules="[ val => val && val.length > 0 || 'Please type something']"
      >
      <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
        As it appears in the provided log.
      </q-tooltip>
      </q-input>

      <q-input
        filled
        v-model="url"
        label="Log URL"
        title=""
        lazy-rules
        dense
        :rules="[
          val => val && val.includes('classic.warcraftlogs.com/reports/')
          || 'Please enter a valid log URL.'
        ]"
      >
        <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
          To a full run or a specific fight, indicated by #fight={fight_num} in the URL fragment
        </q-tooltip>
      </q-input>

      <q-select
        filled
        v-model="defiance_points"
        label="Points in Defiance"
        :options="options"
        lazy-rules
        dense
        title=""
        :rules="[
          val => (val && 0 <= val <= 5) || 'Invalid number of defiance points. 0 through 5, bro'
        ]"
      >
        <template v-slot:prepend>
          <q-icon name="app:defiance" title="" />
        </template>
        <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
          How many points the character has in defiance.
        </q-tooltip>
      </q-select>

      <q-select
        filled
        v-model="bosses"
        label="(Optional) Bosses"
        :options="all_bosses"
        lazy-rules
        use-chips
        stack-label
        dense
        multiple
        title=""
      >
        <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
          For a full report, filter which bosses you are interested in viewing data for.
        </q-tooltip>
      </q-select>
     <div class="row">
      <q-input
        filled
        class="col-4 col-sm-4 q-ma-sm"
        v-model="enemies_in_combat"
        label="(Optional) Enemies Nearby/In Combat"
        :options="options"
        lazy-rules
        dense
        title=""
        :rules="[
            val => (val && !isNaN(val) && val <= 10 && val > 0) || 'Be reasonable. 1-10'
          ]"
        >
          <template v-slot:prepend>
            <q-icon name="app:bs" title="" size="20px" />
          </template>
          <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
            Enemies to split threat with, assuming all hits for now
          </q-tooltip>
        </q-input>
        <q-input
          filled
          class="col-4 col-sm-4 q-ma-sm"
          v-model="friendlies_in_combat"
          label="(Optional) Friendlies Nearby/In Combat"
          lazy-rules
          title=""
          dense
          :rules="[
            val => (val && !isNaN(val && val <= 10 && val > 0) ) || 'Be reasonable. 1-10.'
          ]"
        >
          <template v-slot:prepend>
            <q-icon name="app:bs" title="" size="20px"/>
          </template>
          <q-tooltip :delay="1000" anchor="bottom middle" self="top middle" class="q-mt-md">
            Friendlies in combat. Once again, assuming all hits
          </q-tooltip>
        </q-input>
        <q-toggle
          class="col-2 col-sm-2 q-ma-sm"
          v-model="t1"
          label="(Optional) Tier 1 Set Bonus?"
          lazy-rules
          title=""
          dense
        >
          <template v-slot:prepend>
            <q-icon name="app:t1" title="" size="20px"/>
          </template>
          <q-tooltip :delay="1000" anchor="bottom middle" self="top middle">
            Apply the Tier 1 Sunder Armor bonus?
          </q-tooltip>
        </q-toggle>
      </div>


      <div>
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
            THIS IS A WORK IN PROGRESS. THESE RESULTS ARE ESTIMATIONS. <br/>
          </span><br/>
          <span class="h6 text-accent">
            To contribute, report bugs, or propose features, see <router-link :to="'About'" class="text-accent text-weight-bold">about</router-link>
    </span>
    <threat-result class="q-mt-sm q-mb-sm" v-if="this.results" :results="this.results"/>
    <q-expansion-item
      caption="Instructions"
      :default-opened="false"
      class="row-2 q-ma-lg justify-left bg-secondary shadow-4">
      <q-card>
        <q-card-section>
          Enter your character's name exactly as it appears on the logs.<br/>
          Provide a URL to your raid log. <br/>
          Full raid logs provided will be broken down per-encounter. <br/><br/>
          Specific fights (indicated by #fight={fight_num}) on the end of the URL will be processed
          individually unless specific bosses are selected. <br/><br/>
          As of right now, the calculator assumes the player is a tank and applies the defensive stance modifier to threat of all abilities castable from D Stance. DPS Warriors coming soon.<br/><br/>
          Note: For encounters with multiple enemies, the calculation does not differentiate between them (yet) so threat values are not representative of TPS for the actual named boss. <br/>
          Instead, it represents total TPS for <strong>every</strong> enemy fought during the same time window as the boss.
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
  name: 'WarriorCalculateForm',
  loading: true,
  data: () => {
      return {
          player_name: null,
          url: null,
          defiance_points: 5,
          enemies_in_combat: 1,
          friendlies_in_combat: 1,
          bosses: null,
          t1: false,
          options: [
              5, 4, 3, 2, 1, 0
          ],
          all_bosses: [
              'Lucifron', 'Magmadar', 'Gehennas', 'Garr',
              'Baron Geddon', 'Shazzrah', 'Golemagg the Incinerator',
              'Majordomo Executus', 'Ragnaros', 'Onyxia'
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
    submit() {
        this.errorState = false;
        this.errorMsg = null;
        this.results = null;
        this.is_loading = true;
        axios
        .post(process.env.VUE_APP_API_URL + '/api/v1/calculate', {
          url: this.url,
          player_name: this.player_name,
          defiance_points: this.defiance_points,
          bosses: this.bosses,
          friendlies_in_combat: this.friendlies_in_combat,
          enemies_in_combat: this.enemies_in_combat,
          t1_set: this.t1,
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
};
</script>
