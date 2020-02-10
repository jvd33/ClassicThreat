<template>
  <q-layout view="hHh lpR lFf">
    <link href="https://fonts.googleapis.com/css?family=Muli&display=swap" rel="stylesheet"/>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="public/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="public/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <q-header elevated class="bg-primary fixed-top" height-hint="98">
      <q-toolbar>
        <q-btn flat @click="drawer = !drawer" round dense material icon="menu" />
        <q-toolbar-title>Classic Threat Tools</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawer"
      class="fixed-left z-max"
      show-if-above
      elevated
      :width="200"
      :breakpoint="500"
    >

        <q-list v-for="(menuItem, index) in menuList" :key="index">
        <q-expansion-item
          expand-separator
          :icon=menuItem.icon
          :label=menuItem.label
          default-opened
          v-if="menuItem.label === 'Calculators'"
          group="calculators"
        >
            <q-list v-for="(calc, idx) in calculators" :key="idx">
              <q-item :to="calc.path"
                      exact v-ripple
                      :inset-level=".5"
              >
                <q-item-section avatar>
                  <q-icon :name="calc.icon" />
                </q-item-section>
                <q-item-section>
                  {{ calc.label }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
        <q-expansion-item
          expand-separator
          :icon=menuItem.icon
          :label=menuItem.label
          default-opened
          v-if="menuItem.label === 'Rankings'"
          group="rankings"
        >
            <q-list v-for="(ranking, idx) in rankings" :key="idx">
              <q-item :to="ranking.path"
                      exact v-ripple
                      :inset-level=".5"
              >
                <q-item-section avatar>
                  <q-icon :name="ranking.icon" />
                </q-item-section>
                <q-item-section>
                  {{ ranking.label }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
          <q-item :to="menuItem.path" exact v-ripple v-if="menuItem.label !== 'Calculators' && menuItem.label !== 'Rankings'">
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
      <q-page-scroller position="bottom-right" :scroll-offset="400" :offset="[30, 60]">
      <q-btn icon="keyboard_arrow_up" color="primary" />
    </q-page-scroller>
    </q-page-container>
  </q-layout>
</template>
<script>

import defiance from './assets/defiance.png';
import bt from './assets/bloodthirst.png';
import shield_slam from './assets/shield_slam.png';
import warr from './assets/wow_flat_warrior.png';
import druid from './assets/wow_flat_druid.png';
import hunter from './assets/wow_flat_hunter.png';
import mage from './assets/wow_flat_mage.png';
import paladin from './assets/wow_flat_paladin.png';
import priest from './assets/wow_flat_priest.png';
import rogue from './assets/wow_flat_rogue.png';
import shaman from './assets/wow_flat_shaman.png';
import warlock from './assets/wow_flat_warlock.png';
import hs from './assets/heroic_strike.png';
import dstance from './assets/dstance.png';
import sunder from './assets/sunder.png';
import demo from './assets/demo_shout.png';
import bs from './assets/battle_shout.png';
import rage from './assets/rage.png';
import tc from './assets/thunder_clap.png';
import execute from './assets/execute.png';
import goa from './assets/goa.png';
import healing from './assets/heal.png';
import t1 from './assets/t1.png';
import revenge from './assets/revenge.png';
import taunt from './assets/taunt.png';
import cleave from './assets/cleave.png';
import tranq from './assets/tranq.png';
import horde from './assets/horde.png';
import alliance from './assets/alliance.png';
import hamstring from './assets/hamstring.png';
import shield_bash from './assets/shield_bash.png';
import disarm from './assets/disarm.png';
import zerk_stance from './assets/zerk_stance.png';
import battle_stance from './assets/battle_stance.png';
import mb from './assets/mb.png';
import maul from './assets/maul.png';
import swipe from './assets/swipe.png';
import cower from './assets/cower.png';
import demoRoar from './assets/demoRoar.png';
import cat from './assets/cat.png';
import bear from './assets/bear.png';
import ff from './assets/ff.png';
import fi from './assets/fi.png';

export default {
  data() {
    return {
        drawer: false,
        base: '/',
        custom_icons: {
          'app:taunt': 'img:' + taunt,
          'app:defiance': 'img:' + defiance,
          'app:bt': 'img:' + bt,
          'app:ss': 'img:' + shield_slam,
          'app:warr': 'img:' + warr,
          'app:hs': 'img:' + hs,
          'app:dstance': 'img:' + dstance,
          'app:sunder': 'img:' + sunder,
          'app:demo': 'img:' + demo,
          'app:rage': 'img:' + rage,
          'app:tc': 'img:' + tc,
          'app:execute': 'img:' + execute,
          'app:goa': 'img:' + goa,
          'app:heals': 'img:' + healing,
          'app:t1': 'img:' + t1,
          'app:revenge': 'img:' + revenge,
          'app:bs': 'img:' + bs,
          'app:druid': 'img:' + druid,
          'app:hunter': 'img:' + hunter,
          'app:mage': 'img:' + mage,
          'app:paladin': 'img:' + paladin,
          'app:priest': 'img:' + priest,
          'app:rogue': 'img:' + rogue,
          'app:shaman': 'img:' + shaman,
          'app:warlock': 'img:' + warlock,
          'app:tranq': 'img:' + tranq,
          'app:cleave': 'img:' + cleave,
          'app:horde': 'img:' + horde,
          'app:alliance': 'img:' + alliance,
          'app:battle_stance': 'img:' + battle_stance,
          'app:zerk_stance': 'img:' + zerk_stance,
          'app:shield_bash': 'img:' + shield_bash,
          'app:disarm': 'img:' + disarm,
          'app:hamstring': 'img:' + hamstring,
          'app:mb': 'img:' + mb,
          'app:ff': 'img:' + ff,
          'app:bear': 'img:' + bear,
          'app:cat': 'img:' + cat,
          'app:maul': 'img:' + maul,
          'app:swipe': 'img:' + swipe,
          'app:cower': 'img:' + cower,
          'app:demoRoar': 'img:' + demoRoar,
          'app:fi': 'img:' + fi,
        },

        calculators: [
          {
            icon: 'app:warr',
            label: 'Warrior',
            separator: true,
            path: '/warrior'
          },
          {
            icon: 'app:druid',
            label: 'Druid',
            separator: true,
            path: '/druid'
          },
        ],
        rankings: [
          {
            icon: 'app:warr',
            label: 'Warrior',
            separator: true,
            path: '/rankings/warrior',
            class: 'Warrior',
          },
          {
            icon: 'app:druid',
            label: 'Druid',
            separator: true,
            path: '/rankings/druid',
            class: 'Druid',
          },
        ],

        menuList: [
          {
            icon: 'assessment',
            label: 'Calculators',
            separator: true,
          },
          {
            icon: 'score',
            label: 'Rankings',
            separator: true,
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
            path: '/about',

          },
        ],
    };
  },
  created() {
    this.$q.dark.set(true);
    this.$q.iconMapFn = (iconName) => {
      const icon = this.custom_icons[iconName];
      if (icon !== void 0) {
        return { icon: icon, size: 'sm' }
      }
    }
  },
};
</script>
