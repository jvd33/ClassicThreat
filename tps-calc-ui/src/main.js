import Vue from 'vue';
import VueRouter from 'vue-router'
import App from './App.vue';
import './quasar';
import WarriorCalculateForm from './components/WarriorCalculateForm.vue';
import DruidCalculateForm from './components/DruidCalculateForm.vue';
import WarriorThreatResult from "./components/WarriorThreatResult";
import DruidThreatResult from "./components/DruidThreatResult";
import DPSThreat from "./components/DPSThreatComponent.vue";
import About from './components/About.vue';
import CalculationDetails from './components/CalculationDetails.vue';

const routes = [
  {
    path: '/',
    alias: '/warrior',
    component: WarriorCalculateForm,
  },
  {
    path: '/druid',
    component: DruidCalculateForm,
  },
  {
    path: '/details',
    component: CalculationDetails,
  },
  {
    path: '/about',
    component: About,
  },
];

const router = new VueRouter({
  routes,
  mode: 'history'
});

Vue.config.productionTip = false;
Vue.use(VueRouter);

Vue.component('warr-threat-result', WarriorThreatResult);
Vue.component('dps-threat-result', DPSThreat);
Vue.component('druid-threat-result', DruidThreatResult);
new Vue({
  router,
  render: h => h(App),

}).$mount('#app');
