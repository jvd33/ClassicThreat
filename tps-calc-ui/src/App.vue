<template>
  <q-layout view="hHh lpR lFf">
    <link rel="preconnect" href="https://fonts.googleapis.com/" crossorigin>
    <link rel="preload" href="https://fonts.googleapis.com/css?family=Muli&display=swap" as="style" crossorigin/>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Muli&display=swap" crossorigin/>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="public/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="public/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <q-header elevated class="bg-primary fixed-top" height-hint="98">
      <q-toolbar>
        <q-btn flat @click="drawer = !drawer" round dense material icon="menu" />
        <q-toolbar-title>ClassicThreat</q-toolbar-title>
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
      <span class="text-primary q-pb-lg col-auto col-sm wrap-auto text-h6 text-italic">
        Feb 20 Update: Now supports calculating threat of wipes + performance improvements!
        <a href="https://github.com/jvd33/ClassicThreat/releases/tag/V2.0" class="text-primary">View the Release</a>
      </span>
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
import freedom from './assets/freedom.png';
import holyshield from './assets/holyshield.png';
import kings from './assets/kings.png';
import might from './assets/might.png';
import rf from './assets/rf.png';
import sac from './assets/sac.png';
import salv from './assets/salv.png';
import sealofwisdom from './assets/sealofwisdom.png';
import sealoflight from './assets/sealoflight.png';
import bop from './assets/bop.png';
import righteousness from './assets/righteousness.png';
import cleanse from './assets/cleanse.png';
import light from './assets/light.png';
import sanctuary from './assets/sanctuary.png';
import holylight from './assets/holylight.png';
import thorns from './assets/thorns.png';
import immo from './assets/immo.png';
import melee from './assets/melee.png';
import overpower from './assets/overpower.png';
import moonfire from './assets/moonfire.png';
import rake from './assets/rake.png';
import tf from './assets/tf.png';
import slam from './assets/slam.png';
import frd from './assets/frd.png';
import shred from './assets/shred.png';
import rip from './assets/rip.png';
import fb from './assets/fb.png';
import ww from './assets/ww.png';
import spike from './assets/spike.png';
import manapot from './assets/manapot.png';
import shoot from './assets/shoot.png';
import defaultability from './assets/default.png';
import sapper from './assets/sapper.png';
import claw from './assets/claw.png';
import consecrate from './assets/consecrate.png';
import retaura from './assets/retaura.png';
import judgement from './assets/judgement.png';

export default {
  meta: {
    title: 'Home',
    titleTemplate: title => `${title} | Classic Threat`,
    htmlAttr: {
      lang: 'en',
      amp: true
    },
  },
  data() {
    return {
        drawer: false,
        base: '/',
        custom_icons: {
          'app:shoot': 'img:' + shoot,
          'app:immo': 'img:' + immo,
          'app:overpower': 'img:' + overpower,
          'app:rake': 'img:' + rake,
          'app:tf': 'img:' + tf,
          'app:shred': 'img:' + rake,
          'app:slam': 'img:' + slam,
          'app:frd': 'img:' + frd,
          'app:rip': 'img:' + rip,
          'app:fb': 'img:' + fb,
          'app:ww': 'img:' + ww,
          'app:spike': 'img:' + spike,
          'app:melee': 'img:' + melee,
          'app:thorns': 'img:' + thorns,
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
          'app:bop': 'img:' + bop,
          'app:cleanse': 'img:' + cleanse,
          'app:freedom': 'img:' + freedom,
          'app:holyshield': 'img:' + holyshield,
          'app:kings': 'img:' + kings,
          'app:might': 'img:' + might,
          'app:rf': 'img:' + rf,
          'app:righteousness': 'img:' + righteousness,
          'app:sac': 'img:' + sac,
          'app:salv': 'img:' + salv,
          'app:sealoflight': 'img:' + sealoflight,
          'app:sealofwisdom': 'img:' + sealofwisdom,
          'app:light': 'img:' + light,
          'app:sanctuary': 'img:' + sanctuary,
          'app:holylight': 'img:' + holylight,
          'app:manapot': 'img:' + manapot,
          'app:defaultability': 'img:' + defaultability,
          'app:sapper': 'img:' + sapper,
          'app:claw': 'img:' + claw,
          'app:consecrate': 'img:' + consecrate,
          'app:judgement': 'img:' + judgement,
          'app:retaura': 'img:' + retaura,
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
          {
            icon: 'app:paladin',
            label: 'Paladin',
            separator: true,
            path: '/paladin'
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
          {
            icon: 'app:paladin',
            label: 'Paladin',
            separator: true,
            path: '/rankings/paladin',
            class: 'Paladin',
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
            label: 'Threat Values',
            separator: true,
            path: '/threatvalues'
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
