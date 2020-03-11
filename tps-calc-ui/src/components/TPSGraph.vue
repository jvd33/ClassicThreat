<template>
  <q-page class="q-pa-sm col-12 col-sm-12 text-center" style="min-height: inherit">
    <apexchart type="area" :options="options" :series="series"></apexchart>
  </q-page>
</template>

<style>
</style>

<script>
import axios from 'axios';

export default {
name: 'TPSGraph',
  props: ['boss_id'],
  data () {
    return {
      name: 'TPSGraph',
      errorState: false,
      errorMsg: null,
      series: [],
      is_loading: true,
      options: {
        chart: {
          type: 'area',
          stacked: true,
        },
        zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
        },
        toolbar: {
          autoSelected: 'zoom'
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: 'smooth'
        },
        theme: {
          palette: 'palette7',
        },
        legend: {
          position: 'top',
        },
        xaxis: {
          type: 'numeric',
          min: 0,
          tickAmount: .25,
        },
        markers: {
          size: 0,
          style: 'hollow',
        },
      },
    }
  },
  mounted() {
    axios
    .get(process.env.VUE_APP_API_URL + '/api/v1/events/yvWQ4xrM3pcKDTfL/Aemin/4')
    .then(response => {
      this.series = response.data.events
      let anno = {xaxis: []}
      response.data.aggro_windows.forEach((window) => {
        console.log(window)
        anno.xaxis.push({
            x: window[0],
            x2: window[1],
            fillColor: '#B3F7CA',
            opacity: 1,
            label: {
              borderColor: '#B3F7CA',
              style: {
                fontSize: '10px',
                color: '#fff',
                background: '#00E396',
              },
              text: 'Has Boss Aggro',
            },
          });
      });
      this.options.annotations = anno;
      console.log(this.options)
      this.loading = false;
    })
    .catch(error => {
        this.errorState = true;
        this.errorMsg = error.response ?
          error.response.data.details : 'Unexpected error. Try again later.';
    }).finally(() => this.is_loading = false);
  },




  methods: {
    getIcon(ability) {
      if (ability.includes('Spike')) return 'app:spike';
      if (ability.includes('Thunderfury')) return 'app:tf';
      if (ability.includes('Shoot')) return 'app:shoot';
      if (ability.includes('Judgement')) return 'app:judgement';
      if (ability.includes('Blessing of Might')) return 'app:might';
      if (ability.includes('Blessing of Sacrifice')) return 'app:sac';
      if (ability.includes('Blessing of Kings')) return 'app:kings';
      if (ability.includes('Blessing of Sanctuary')) return 'app:sanctuary';
      if (ability.includes('Blessing of Protection')) return 'app:bop';
      if (ability.includes('Blessing of Light')) return 'app:light';
      if (ability.includes('Blessing of Salvation')) return 'app:salv';

      switch(ability) {
        case 'Bloodthirst': return 'app:bt';
        case 'Shield Slam': return 'app:ss';
        case 'Heroic Strike': return 'app:hs';
        case 'Defensive Stance': return 'app:dstance';
        case 'Sunder Armor': return 'app:sunder';
        case 'Demoralizing Shout': return 'app:demo';
        case 'Battle Shout': return 'app:bs';
        case 'Resource Gain': return 'app:rage';
        case 'Thunder Clap': return 'app:tc';
        case 'Execute': return 'app:execute';
        case 'Gift of Arthas': return 'app:goa';
        case 'Healing Done': return 'app:heals';
        case 'Revenge': return 'app:revenge';
        case 'Cleave': return 'app:cleave';
        case 'Maul': return 'app:maul';
        case 'Swipe': return 'app:swipe';
        case 'Cower': return 'app:cower';
        case 'Faerie Fire': return 'app:ff';
        case 'Faerie Fire (Feral)': return 'app:ff';
        case 'Bear Form': return 'app:bear';
        case 'Cat Form': return 'app:cat';
        case 'Demoralizing Roar': return 'app:demoRoar';
        case 'Cleanse': return 'app:cleanse';
        case 'Righteous Fury': return 'app:rf';
        case 'Blessing Of Freedom': return 'app:freedom';
        case 'Paladin Spell Healing': return 'app:holylight';
        case 'Mana Gain': return 'app:manapot';
        case 'Force Reactive Disk': return 'app:frd';
        case 'Rip': return 'app:rip';
        case 'Rake': return 'app:rake';
        case 'Thorns': return 'app:thorns';
        case 'Whirlwind': return 'app:ww';
        case 'Slam': return 'app:slam';
        case 'Shred': return 'app:shred';
        case 'Overpower': return 'app:overpower';
        case 'Melee': return 'app:melee';
        case 'Oil of Immolation': return 'app:immo';
        case 'Claw': return 'app:claw';
        case 'Consecration': return 'app:consecrate';
        case 'Retribution Aura': return 'app:retaura';
        case 'Seal of Wisdom': return 'app:sealofwisdom';
        case 'Seal of Righteousness': return 'app:righteousness';
        case 'Seal of Light': return 'app:sealoflight';
        case 'Sacred Shield': return 'app:holyshield';
        case 'Holy Shield': return 'app:holyshield';
        case 'Essence of the Red': return 'app:ba';
        case 'Hammer of Wrath': return 'app:hammerofwrath';
        case 'Goblin Sapper Charge': return 'app:sapper';
        case 'Paladin Healing': return 'app:holylight';

        default: return 'app:defaultability';
      };
    },
  },
};
</script>
