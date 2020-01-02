import Vue from 'vue';
import VueRouter from 'vue-router'
import App from './App.vue';
import './quasar';
import CalculateForm from './components/CalculateForm.vue';
import ThreatResult from "./components/ThreatResult";
import About from './components/About.vue';
import CalculationDetails from './components/CalculationDetails.vue';

const routes = [
  {
    path: '/',
    component: CalculateForm,
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
new Vue({
  router,
  render: h => h(App),

}).$mount('#app');
