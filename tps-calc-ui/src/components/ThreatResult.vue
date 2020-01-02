<template>
  <q-page>
    <q-list bordered class="rounded-borders" v-for="(value, name) in results" :key="name">
      <q-expansion-item :caption="name" class="q-pa-sm">
        <q-card>
          <q-card-section>
              <span class="text-h5 text-center">
                Raw Estimated Threat Per Second: <strong class="text-h4 text-primary">{{value.tps.toPrecision(5)}}</strong>
              <br/>
                <br/>
              </span>
              <span class="text-center">Data used for calculation: <br/><br/> {{value}}</span>
          </q-card-section>
        </q-card>
      </q-expansion-item>

    </q-list>
  </q-page>
</template>
<script>
export default {
  name: 'ThreatResult',
    props: ['results']
};
</script>
