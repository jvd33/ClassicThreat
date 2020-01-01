import VueRouter from 'vue';
import CalculateForm from './components/CalculateForm.vue';
import About from './components/About.vue';

const routes = [
  {
    path: '/',
    component: CalculateForm,
    children: [
      { path: 'about', component: About },
    ],
  },
];

const router = new VueRouter({
  routes
});

export default router
