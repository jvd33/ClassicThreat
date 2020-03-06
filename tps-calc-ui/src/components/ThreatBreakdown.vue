<template>
  <q-page class="q-pa-sm col-12 col-sm-12 text-center" style="min-height: inherit">
    <span class="text-h5 text-white col-12 col-sm-12">
      Threat Breakdown
    </span>
    <q-table
      :data="events"
      :columns="breakdown_cols"
      :rows-per-page-options="[0]"
      :pagination.sync="pagination"
      row-key="guid"
      :grid="$q.screen.xs"
      class="col-12 col-12-sm q-mt-md q-mb-md"
      hide-bottom
    >
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
            <q-icon
              :name="getIcon(props.row.name)"
              size="20px"
              :label="props.row.name"
              class="q-ma-sm"
              title=""
            /> {{props.row.name}}
        </q-td>
      </template>

      <template v-slot:item="props">
        <div
          class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3 grid-style-transition"
        >
          <q-card>
            <q-card-section>
              <q-icon
                :name="getIcon(props.row.name)"
                size="20px"
                :label="props.row.name"
                title=""
              /> {{props.row.name}}
            </q-card-section>
            <q-separator color="primary" inset></q-separator>
            <q-list dense class="text-left">
              <q-item v-for="col in props.cols.filter(col => sm_cols.includes(col.name))" :key="col.name">
                <q-item-section>
                  <q-item-label>{{ col.label }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label caption>{{ col.value }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </template>

    </q-table>
  </q-page>
</template>

<style>
</style>

<script>
export default {
  props: ['events', 'time'],
  name: 'ThreatBreakdown',
  meta: {
    title: '',
    htmlAttrs: {
      lang: 'en',
      amp: true
    }
  },
  methods: {
    getIcon(ability) {
      if (ability.includes('Spike')) return 'app:spike';
      if (ability.includes('Thunderfury')) return 'app:tf';
      if (ability.includes('Shoot')) return 'app:shoot';
      if (ability.includes('Judgement')) return 'app:judgement';
      if (ability.includes('Blessing of Might')) return 'app:might';
      if (ability.includes('Blessing of Sacrifice')) return 'app:sac';
      if (ability.includes('Blessing of Kings')) return 'app:kings';
      if (ability.includes('Blessing of Sanctuary')) return 'app:sanctuary';
      if (ability.includes('Blessing of Protection')) return 'app:bop';
      if (ability.includes('Blessing of Light')) return 'app:light';
      if (ability.includes('Blessing of Salvation')) return 'app:salv';

      switch(ability) {
        case 'Bloodthirst': return 'app:bt';
        case 'Shield Slam': return 'app:ss';
        case 'Heroic Strike': return 'app:hs';
        case 'Defensive Stance': return 'app:dstance';
        case 'Sunder Armor': return 'app:sunder';
        case 'Demoralizing Shout': return 'app:demo';
        case 'Battle Shout': return 'app:bs';
        case 'Resource Gain': return 'app:rage';
        case 'Thunder Clap': return 'app:tc';
        case 'Execute': return 'app:execute';
        case 'Gift of Arthas': return 'app:goa';
        case 'Healing Done': return 'app:heals';
        case 'Revenge': return 'app:revenge';
        case 'Cleave': return 'app:cleave';
        case 'Maul': return 'app:maul';
        case 'Swipe': return 'app:swipe';
        case 'Cower': return 'app:cower';
        case 'Faerie Fire': return 'app:ff';
        case 'Faerie Fire (Feral)': return 'app:ff';
        case 'Bear Form': return 'app:bear';
        case 'Cat Form': return 'app:cat';
        case 'Demoralizing Roar': return 'app:demoRoar';
        case 'Cleanse': return 'app:cleanse';
        case 'Righteous Fury': return 'app:rf';
        case 'Blessing Of Freedom': return 'app:freedom';
        case 'Paladin Spell Healing': return 'app:holylight';
        case 'Mana Gain': return 'app:manapot';
        case 'Force Reactive Disk': return 'app:frd';
        case 'Rip': return 'app:rip';
        case 'Rake': return 'app:rake';
        case 'Thorns': return 'app:thorns';
        case 'Whirlwind': return 'app:ww';
        case 'Slam': return 'app:slam';
        case 'Shred': return 'app:shred';
        case 'Overpower': return 'app:overpower';
        case 'Melee': return 'app:melee';
        case 'Oil of Immolation': return 'app:immo';
        case 'Claw': return 'app:claw';
        case 'Consecration': return 'app:consecrate';
        case 'Retribution Aura': return 'app:retaura';
        case 'Seal of Wisdom': return 'app:sealofwisdom';
        case 'Seal of Righteousness': return 'app:righteousness';
        case 'Seal of Light': return 'app:sealoflight';
        case 'Sacred Shield': return 'app:holyshield';
        case 'Holy Shield': return 'app:holyshield';
        case 'Essence of the Red': return 'app:ba';
        case 'Hammer of Wrath': return 'app:hammerofwrath';
        case 'Goblin Sapper Charge': return 'app:sapper';
        case 'Paladin Healing': return 'app:holylight';

        default: return 'app:defaultability';
      };
    },
  },
  data() {
    return {
      pagination: {
          page: 1,
          rowsPerPage: 0,
      },
      sm_cols: ['percentage_threat', 'modified_tps', 'hits', 'casts_per_minute'],
      breakdown_cols: [
        { name: 'name', align: 'left', label: 'Threat Source', field: row => row.name, sortable: true },
        { name: 'percentage_threat', align: 'left', label: '% of Threat', field: row => row.percentage_threat, format: val => `${val.toPrecision(4)}%`, sortable: true },
        { name: 'modified_tps', align: 'left', label: 'Total TPS', field: row => row.modified_threat/this.time, format: val => val.toPrecision(4), sortable: true },
        { name: 'modified_threat', align: 'left', label: 'Total Threat', field: row => row.modified_threat, format: val => val.toPrecision(7), sortable: true },
        { name: 'hits', align: 'left', label: 'Hits', field: row => row.hits, sortable: true },
        { name: 'count', align: 'left', label: 'Casts', field: row => row.count > 0 ? row.count : '--', sortable: true },
        { name: 'casts_per_minute', align: 'left', label: 'CPM', field: row => row.count/(this.time/60), format: val => val > 0 ? val.toPrecision(3) : '--', sortable: true },
      ],
    }
  }
};
</script>
