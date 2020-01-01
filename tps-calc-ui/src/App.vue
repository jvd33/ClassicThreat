<template>
  <q-layout view="hHh lpR lFr">

    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo/svg/quasar-logo.svg">
          </q-avatar>
          Classic Threat Estimator
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer reveal bordered class="bg-grey-8 text-white">
      <q-toolbar>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script>
export default {
  data() {
    return {
    };
  },
  created() {
    this.$q.dark.set(true);
  },
};
</script>
