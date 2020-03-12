<template>
  <q-page class="q-pa-sm col-12 col-sm-12" style="min-height: inherit;" v-if="series !== undefined">
    <q-separator color="primary q-ma-sm" inset></q-separator>
    <apexchart type="area" height="700" :options="options" :series="series"></apexchart>
  </q-page>
</template>

<style>
</style>

<script>
import axios from 'axios';
import moment from 'moment';

export default {
name: 'TPSGraph',
  props: ['boss_id', 'report_id', 'player_name'],
  data () {
    return {
      name: 'TPSGraph',
      errorState: false,
      errorMsg: null,
      series: undefined,
      is_loading: true,
      options: {},
    }
  },
  mounted() {
    axios
    .get(process.env.VUE_APP_API_URL + `/api/v1/events/${this.report_id}/${this.player_name}/${this.boss_id}`)
    .then(response => {

      let options = {
        responsive: [{
            breakpoint: 1000,
            options: {
              chart: {
                toolbar: {
                  show: false,
                },
              },
              title: {
                style: {
                  fontSize:  '16px',
                },
              },
              yaxis: {
                labels: {
                  show: false,
                }
              },
              xaxis: {
                labels: {
                  style: {
                    fontSize: '12px',
                  },
                }
              },
            },
        }],
        chart: {
          foreColor: '#fff',
          toolbar: {
            show: true,
            autoSelected: 'zoom',
            tools: {
              download: false,
              selection: true,
              zoom: true,
              zoomin: true,
              zoomout: false,
              pan: false,
              reset: true
            },
          },
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },
          animations: {
            enabled: true,
            easing: 'linear',
            speed: 500,
            animateGradually: {
                enabled: true,
                delay: 100
            },
            dynamicAnimation: {
                enabled: true,
                speed: 100
            }
          },
        },
        tooltip: {
          theme: 'dark',
          shared: false,
          followCursor: true,
          y: {
            formatter: function(value, { series, seriesIndex, dataPointIndex, w }) {
              return `${value} Threat`
            }
          },
          x: {
            format: 'mm:ss:fff',
          },
        },
        stroke: {
          curve: 'smooth',
          width: 1.5,
        },
        fill: {
          type: 'gradient',
          gradient: {
                shade: 'dark',
                type: "vertical",
                shadeIntensity: 0.25,
                inverseColors: true,
                opacityFrom: .7,
                opacityTo: .9,
                stops: [0, 50, 80, 100],
                colorStops: []
            },
        },
        title: {
            text: 'Threat Per Second By Ability',
            align: 'center',
            margin: 20,
            floating: false,
            style: {
              fontSize:  '25px',
              fontWeight:  'bold',
              fontFamily: 'Muli',
              color:  '#fff'
            },
        },
        legend: {
          position: 'bottom',
          horizontalAlign: 'center',
          fontSize: 16,
          fontWeight: 500,
          fontFamily: 'Muli',
          markers: {
            width: '12px',
            height: '12px',
          },
        },
        dataLabels: {
          enabled: false,
        },
        colors: [
          '#b55400',
          '#bd6c21',
          '#c5833c',
          '#cd9957',
          '#d5ae74',
          '#ddc293',
          '#e7d6b2',
          '#f2ead3',
          '#fffdf5',
          '#a28472',
          '#9c8c82',
          '#939393'
        ],
        yaxis: {
          type: 'numeric',
          labels: {
            show: true,
            style: {
              fontSize: '14px',
              fontFamily: 'Muli',
              fontWeight: 400,
            },
          },
          title: {
            text: 'Threat',
            style: {
              fontFamily: 'Muli',
              fontSize: '18px',
              fontWeight: 400,
            },

          },
        },
        xaxis: {
          type: 'datetime',
          labels: {
            show: true,
            formatter: function (value, timestamp) {
              let x = new Date(timestamp)
              return moment(new Date(timestamp)).format('mm:ss:SSS')
            },
            style: {
              fontSize: '14px',
              fontFamily: 'Muli',
              fontWeight: 400,
            },
          },
          axisTicks: {
            show: true,
            borderType: 'solid',
            height: 10,
          },
          max: new Date(response.data.total_time),
          title: {
            text: 'Elapsed Time',
            style: {
              fontFamily: 'Muli',
              fontSize: '18px',
              fontWeight: 400,
            },

          },
        },
      };

      this.series = response.data.events
      let anno = {xaxis: [], position: 'back'}
      response.data.aggro_windows.forEach((window) => {
        anno.xaxis.push({
            x: new Date(window[0]).getTime(),
            x2: new Date(window[1]).getTime(),
            fillColor: '#b55400',
            opacity: .2,
            label: {
              borderColor: '#121212',
              position: 'top',
              textAnchor: 'right',
              offsetY: 15,
              offsetX: 10,
              style: {
                fontSize: '14px',
                color: '#fff',
                background: '#121212',
                fontFamily: 'Muli',
              },
              orientation: 'horizontal',
              text: anno.xaxis.length > 0 ? '': 'Has Boss Aggro',
            },
          });
      });
      options.annotations = anno;
      this.options = options;
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
