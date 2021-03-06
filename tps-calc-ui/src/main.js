import Vue from 'vue';
import VueRouter from 'vue-router'
import VueGtag from "vue-gtag";
import VueApexCharts from "vue-apexcharts";
import App from './App.vue';
import './quasar';
import WarriorCalculateForm from './components/WarriorCalculateForm.vue';
import DruidCalculateForm from './components/DruidCalculateForm.vue';
import PaladinCalculateForm from './components/PaladinCalculateForm.vue';
import DPSThreat from "./components/DPSThreatComponent.vue";
import About from './components/About.vue';
import CalculationDetails from './components/CalculationDetails.vue';
import ClassRankings from './components/ClassRankings.vue'
import ThreatBreakdown from './components/ThreatBreakdown.vue'
import ThreatResult from './components/ThreatResult.vue';
import TPSGraph from './components/TPSGraph.vue';

const routes = [
  {
    path: '/warrior',
    component: WarriorCalculateForm,
  },
  {
    path: '/druid',
    component: DruidCalculateForm,
  },
  {
    path: '/paladin',
    component: PaladinCalculateForm,
  },
  {
    path: '/threatvalues',
    component: CalculationDetails,
  },
  {
    path: '/',
    alias: '/about',
    component: About,
  },
  {
    path: '/rankings/warrior',
    component: ClassRankings,
    props: {player_class: 'Warrior'},
  },
  {
    path: '/rankings/druid',
    component: ClassRankings,
    props: {player_class: 'Druid'},
  },
  {
    path: '/rankings/paladin',
    component: ClassRankings,
    props: {player_class: 'Paladin'},
  },
];

const router = new VueRouter({
  routes,
  mode: 'history'
});

Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.use(VueGtag, {
  config: { id: "UA-77837329-2" }
});
Vue.use(VueApexCharts);

Vue.component("apexchart", VueApexCharts);
Vue.component('threat-result', ThreatResult);
Vue.component('dps-threat-result', DPSThreat);
Vue.component('tps-graph', TPSGraph);
Vue.component('threat-breakdown', ThreatBreakdown)
new Vue({
  router,
  render: h => h(App),

}).$mount('#app');
