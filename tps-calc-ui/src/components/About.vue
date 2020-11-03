<template>
  <div class="q-pa-md col-12" >
    <div>
      <q-card class="row">

        <q-toolbar-title
          class="text-primary text-h3 vertical-middle col-12"
        >
          <q-avatar size="200px" class="shadow-10 q-ma-md vertical-middle center">
            <q-img :src="require('../assets/nef_circ.png')"/>
          </q-avatar>
          <span class="col-12">
          ClassicThreat</span>
        </q-toolbar-title>
        <q-card-section class="col-12">

          <span class="text-h6 q-pb-lg"> ClassicThreat is a tool meant to help tanks in Classic WoW analyze their performance. <br/> <br/> This application seeks to build on top of the extensive reporting capabilities of Warcraft Logs in an effort to improve tank performance. <br/><br/></span>
          <q-separator horizontal inset=".5" class="q-mb-md"/>
          I no longer play Classic WoW! Maintenace on this app is minimal, but submit an issue on GitHub and I'll get to it.

          <br/><br/>
          Feature Requests and Bug Reports can be submitted on GitHub:
          <a class="text-accent text-weight-bold" href="https://github.com/jvd33/ClassicThreat">
            https://github.com/jvd33/ClassicThreat
          </a>
          <br/><br/>
          Feel free to clone and submit pull requests, I'll approve PRs that fit code standards and add value or new functionality.
          <br/><br/>
          For urgent bugs, feel free to message me on Discord.
          <br/><br/>
          <q-separator horizontal inset=".5" class="q-mb-md"/>
          <span class="text-primary text-h4">Future planned features:<br/></span><br/>
            - Split TPS across individual mobs in the boss encounters (e.g. Lucifron TPS, Flamewaker 1 TPS, Flamewaker 2 TPS) <br/>
            - More set bonuses/modifiers of various kinds, more spell ranks <br/>
            - Comparing against other players previously submitted to ClassicThreat <br/>
            - Non-tank roles
          <span class="text-primary text-h6"><br/>Thanks to:<br/></span>
            - Dhoris/AutumnRain for his great work on the TPS spreadsheet that inspired this<br/>
            - Fight Club/magey's classic-warrior GitHub/libthreat2/everyone who has contributed to our understanding of threat mechanics <br/>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<style>
</style>

<script>
export default {
  name: 'About',
  meta: {
    title: 'About Classic Threat',
    htmlAttrs: {
      lang: 'en',
      amp: true
    },

  },
};
</script>
