import Vue from 'vue';
import VueRouter from 'vue-router'
import App from './App.vue';
import './quasar';
import WarriorCalculateForm from './components/WarriorCalculateForm.vue';
import ThreatResult from "./components/ThreatResult";
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

Vue.component('threat-result', ThreatResult);
Vue.component('dps-threat-result', DPSThreat);
new Vue({
  router,
  render: h => h(App),

}).$mount('#app');
