<template>
  <q-page class="q-pa-md row-12 fit no-wrap overflow-auto" style="position: relative;" >
    <q-toolbar-title
      class="text-primary text-h4 text-weight-bold q-pb-lg"
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
        :rules="[ val => val && val.length > 0 || 'Please type something']"
      >
      <q-tooltip :delay="750" anchor="bottom left" self="bottom left">
        As it appears in the provided log.
      </q-tooltip>
      </q-input>

      <q-input
        filled
        type="url"
        v-model="url"
        label="Log URL"
        title=""
        lazy-rules
        :rules="[
          val => val && val.includes('classic.warcraftlogs.com/reports/')
          || 'Please enter a valid log URL.'
        ]"
      >
        <template v-slot:prepend>
            <q-icon name="link" />
        </template>
        <q-tooltip :delay="750" anchor="bottom left" self="bottom left">
          To a full run or a specific fight, indicated by #fight={fight_num} in the URL fragment
        </q-tooltip>
      </q-input>

      <q-select
        filled
        v-model="defiance_points"
        label="Points in Defiance"
        :options="options"
        lazy-rules
        title=""
        :rules="[
          val => (val && val >= 0 && val <= 5) || 'Invalid number of defiance points. 0 through 5, bro'
        ]"
      >
        <template v-slot:prepend>
          <q-icon name="app:defiance" />
        </template>
        <q-tooltip :delay="750" anchor="bottom left" self="bottom left">
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
        multiple
        title=""
      >
        <q-tooltip :delay="750" anchor="bottom left" self="bottom left">
          For a full report, filter which bosses you are interested in viewing data for.
        </q-tooltip>
      </q-select>

      <div>
        <q-btn label="Estimate" type="submit" color="primary"/>
      </div>
      <div>
        <span class="row-1 text-weight-bold text-negative q-pt-md text-weight-bold bg-secondary"
           v-if="this.errorState"
        >
          {{this.errorMsg}}
        </span>
      </div>
    </q-form>
    <q-expansion-item
      caption="Instructions"
      :default-opened="true"
      class="row-2 q-ma-lg justify-left bg-secondary shadow-4">
      <q-card>
        <q-card-section>
          <span class="h5 text-warning">
            THIS IS A WORK IN PROGRESS. THESE RESULTS ARE ESTIMATIONS. <br/>
          </span><br/>
          <span class="h6 text-accent">
            Contact coandca#1313 on Discord with bug reports or see
            <router-link :to="'About'" class="text-accent text-weight-bold">About</router-link> for more contact methods.
          </span> <br/><br/>
          Enter your character's name exactly as it appears on the logs.<br/>
          Provide a URL to your raid log. <br/>
          Full raid logs provided will be broken down per-encounter. <br/>
          Specific fights (indicted by #fight={fight_num}) on the end of the URL will be processed
          individually unless specific bosses are selected. <br/>
        </q-card-section>
      </q-card>
    </q-expansion-item>

    <threat-result class="row-6 q-pa-sm fit overflow-auto" v-if="this.results" :results="results"/>

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
          bosses: null,
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
        .post(process.env.VUE_APP_API_URL + '/v1/api/calculate', {
          url: this.url,
          player_name: this.player_name,
          defiance_points: this.defiance_points,
          bosses: this.bosses,
        })
        .then(response => {
          this.api_status = response.status;
          this.results = response.data;
          this.is_loading = false;
        })
        .catch(error => {
            this.errorState = true;
            this.errorMsg = error.response ?
              error.response.data.details : 'Unexpected error. Try again later.';
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
