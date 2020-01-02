import Vue from 'vue';

import './styles/quasar.sass';
import '@quasar/extras/material-icons/material-icons.css';
import { Quasar, Loading, Dialog } from 'quasar';

Vue.use(Quasar, {
  components: { /* not needed if importStrategy is not 'manual' */ },
  directives: { /* not needed if importStrategy is not 'manual' */ },
  plugins: {
    Loading,
    Dialog,
  },
  config: {
    loading: { /* Loading defaults */ },
  },
});
