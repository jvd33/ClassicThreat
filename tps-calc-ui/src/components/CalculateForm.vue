<template>
  <div class="q-pa-md" style="max-width: 400px">

    <q-form
      @submit="onSubmit"
      class="q-gutter-md"
    >
      <q-input
        filled
        v-model="character_name"
        label="Character Name:"
        hint="As it appears in the logs"
        lazy-rules
        :rules="[ val => val && val.length > 0 || 'Please type something']"
      />

      <q-input
        filled
        v-model="url"
        label="Log URL:"
        lazy-rules
        :rules="[
          val => val && val.length > 0 && val.includes('classic.warcraftlogs.com/reports/') ||
          'Please enter a valid log URL.'
        ]"
      />

      <div>
        <q-btn label="Submit" type="submit" color="primary"/>
      </div>
    </q-form>

  </div>
</template>

<script>
export default {
  name: 'CalculateForm',
  data() {
    return {
      character_name: null,
      url: null,
    };
  },

  methods: {
    onSubmit() {
      this.$q.notify({
        color: 'green-4',
        textColor: 'white',
        icon: 'cloud_done',
        message: 'Submitted',
      });
    },
  },
};
</script>
