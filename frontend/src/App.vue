<!-- App.vue mit Router -->
<template>
  <div class="finance-app">
    <!-- Navigation mit router-link -->
    <div class="app-navigation">
      <router-link to="/monatsuebersicht">Monatsübersicht</router-link>
      <router-link to="/konfiguration">Feste Posten</router-link>
    </div>
    
    <!-- Router View für den Inhalt -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Styling wie oben */
.finance-app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-navigation {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.app-navigation a {
  padding: 10px 15px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
}

.app-navigation a:hover,
.app-navigation a.router-link-active {
  background-color: #e0e0e0;
}
</style>