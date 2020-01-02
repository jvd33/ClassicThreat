<template>
  <q-layout view="hHh lpR lFf">
    <link href="https://fonts.googleapis.com/css?family=Muli&display=swap" rel="stylesheet"/>
    <q-header elevated class="bg-primary fixed-top" height-hint="98">
      <q-toolbar>
        <q-btn flat @click="drawer = !drawer" round dense material icon="menu" />
        <q-toolbar-title>Classic Threat Estimator</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawer"
      class="fixed-left"
      show-if-above
      elevated
      :width="200"
      :breakpoint="300"
    >

        <q-list v-for="(menuItem, index) in menuList" :key="index">

          <q-item :to="menuItem.path" exact v-ripple>
            <q-item-section avatar>
              <q-icon :name="menuItem.icon" />
            </q-item-section>
            <q-item-section>
              {{ menuItem.label }}
            </q-item-section>
          </q-item>

         <q-separator v-if="menuItem.separator" />

        </q-list>

    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script>
const icons = {
  'app:defiance': 'img:statics/abilities/defiance.png',
  'app:bt': 'img:statics/abilities/bloodthirst.png',
  'app:ss': 'img:statics/assets/abilities/shield_slam.png',
};

const menuList = [
  {
    icon: 'assessment',
    label: 'Estimate',
    separator: true,
    path: '/'
  },
  {
    icon: 'info',
    label: 'Calculation Details',
    separator: true,
    path: '/details'
  },
  {
    icon: 'contacts',
    label: 'About',
    separator: true,
    path: '/about'

  },
];
export default {
  data() {
    return {
        drawer: false,
        menuList,
        base: '/'
    };
  },
  created() {
    this.$q.dark.set(true);
    this.$q.iconMapFn = (iconName) => {
      const icon = icons[iconName];
      if (icon !== void 0) {
        return { icon: icon }
      }
    }
  },
};
</script>
