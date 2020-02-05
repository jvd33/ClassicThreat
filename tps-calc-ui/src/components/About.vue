<template>
  <div class="q-pa-md col-12" >
    <div>
      <q-card>
        <q-card-section>
          Contact me on Discord: <span class="text-primary text-weight-bold text-h6">coandca#1313</span>
          <br/>
          or send gold to Aemin - Skeram US (pls)
          <br/><br/>
          There's a public API, documentation can be viewed at
          <a class="text-accent text-weight-bold" href="/api/v1/docs">
            https://classicthreat.com/api/v1/docs
          </a>. There's very little functionality, but the website is driven by an accessible REST API.
          <br/><br/>
          Feature Requests and Bug Reports can be submitted on GitHub:
          <a class="text-accent text-weight-bold" href="https://github.com/jvd33/ClassicTPSEstimator/issues">
            https://github.com/jvd33/ClassicThreat
          </a>
          <br/><br/>
          Feel free to clone and submit pull requests, I'll approve PRs that fit code standards and add value or new functionality.
          <br/><br/>
          For urgent bugs, feel free to message me on Discord.
          <br/><br/>
          <span class="text-primary text-h4">Future planned features:<br/></span><br/>
            - Split TPS across individual mobs in the boss encounters (e.g. Lucifron TPS, Flamewaker 1 TPS, Flamewaker 2 TPS) <br/>
            - More set bonuses/modifiers of various kinds, more spell ranks <br/>
            - TPS Graphing (Coming Soon!)<br/>
            - Comparing against other players previously submitted to ClassicThreat <br/>
            - Non-tank roles
          <span class="text-primary text-h6">Thanks to:<br/></span>
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
};
</script>
