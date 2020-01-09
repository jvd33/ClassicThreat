<template>
  <div class="q-pa-md col-12" >
    <div>
      <span class="text-h3">About</span>
      <q-card>
        <q-card-section>
          Contact me on Discord: <span class="text-primary text-weight-bold text-h6">coandca#1313</span>
          <br/>
          or send gold to Aemin - Skeram US (pls)
          <br/><br/>
          API Documentation can be viewed
          <a class="text-accent text-weight-bold" href="https://classicthreat.com/api/v1/docs">
            Here
          </a>
          <br/><br/>
          Feature Requests and Bug Reports can be submitted on GitHub: <br/>
          <a class="text-accent text-weight-bold" href="https://github.com/jvd33/ClassicTPSEstimator/issues">
            https://github.com/jvd33/ClassicThreat
          </a>
          <br/><br/>
          Feel free to clone and submit pull requests, I'll approve PRs that fit code standards and add value
          <br/><br/>
          For urgent bugs, feel free to message me on Discord.
          <br/><br/>
          <span class="text-primary text-h4">Future planned features:<br/></span><br/>
            - Calculate DPS needed to rip given the TPS per class<br/>
            - Split TPS across individual mobs in the boss encounters (e.g. Lucifron TPS, Flamewaker 1 TPS, Flamewaker 2 TPS) <br/>
            - Bear tanks<br/>
            - Paladin tanks? (lol memespec)<br/>
            - DPS/TPS correlation, tank survivability, CPM, etc.<br/>
            - Literally any other valuable analysis because this is so much easier than using the WarcraftLogs UI<br/><br/>
          <span class="text-primary text-h4">Thanks to:<br/></span><br/>
            - Fight Club <br/>
            - Dhoris/AutumnRain for his great work on the initial TPS spreadsheet <br/>
            - magey/the classic-warrior GitHub/everyone who contributed for all the mechanics work they've done <br/>
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
